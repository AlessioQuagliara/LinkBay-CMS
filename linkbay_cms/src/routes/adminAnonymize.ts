import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';
import { writeAudit } from '../middleware/audit';

const router = Router();
router.use(requirePermission('admin.view'));

// POST /api/admin/users/:userId/anonymize
router.post('/users/:userId/anonymize', async (req:any, res) => {
  const targetId = Number(req.params.userId);
  if (!targetId) return res.status(400).json({ error: 'invalid_user_id' });
  try {
    // fetch user (global table)
    const user = await knex('users').where({ id: targetId }).first();
    if (!user) return res.status(404).json({ error: 'not_found' });

    // perform anonymization - best-effort within a transaction
    await knex.transaction(async (trx) => {
      // update main users row
      const anonEmail = `user_${targetId}@deleted.local`;
      await trx('users').where({ id: targetId }).update({ email: anonEmail, name: '[Redacted]', address: '[Redacted]', anonymized_at: new Date() });

      // also anonymize related tenant tables that commonly store PII
      const tenantTables = ['customer_profiles', 'orders', 'invoices'];
      for (const t of tenantTables) {
        try {
          const cols = await trx.raw(`SELECT column_name FROM information_schema.columns WHERE table_name = ?`, [t]);
          const colNames = cols && cols.rows ? cols.rows.map((r:any)=>r.column_name) : [];
          const updates: any = {};
          if (colNames.includes('email')) updates.email = anonEmail;
          if (colNames.includes('name')) updates.name = '[Redacted]';
          if (colNames.includes('address')) updates.address = '[Redacted]';
          if (Object.keys(updates).length) await trx(t).where({ user_id: targetId }).update(updates);
        } catch (e) { /* ignore missing tables */ }
      }
    });

    try { await writeAudit('AUDIT.USER_ANONYMIZED', { tenantId: req.tenant ? req.tenant.id : null, userId: req.user ? req.user.id : null, metadata: { target_user: targetId } }); } catch(e){}
    res.json({ success: true });
  } catch (err:any) {
    console.error('anonymize failed', err && err.message);
    res.status(500).json({ error: 'anonymize_failed' });
  }
});

export default router;
