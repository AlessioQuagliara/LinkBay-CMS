import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';
import { writeAudit } from '../middleware/audit';
import zlib from 'zlib';

const router = Router();

// strict rate limiter for DSAR endpoints (per admin user)
import rateLimit from 'express-rate-limit';
const dsarLimiter = rateLimit({ windowMs: 60 * 60 * 1000, max: 5, keyGenerator: (req:any) => `dsar_user_${req.user ? req.user.id : req.ip}`, standardHeaders: true, legacyHeaders: false });

// Helper: gather rows for a given user across common tables
async function gatherGlobalUserData(userId: number) {
  const out: any = {};
  const tables = ['users', 'orders', 'invoices', 'audit_logs'];
  for (const t of tables) {
    try { out[t] = await knex(t).where({ user_id: userId }).select('*'); } catch (e) { out[t] = []; }
  }
  return out;
}

// Helper: gather tenant-scoped data by enumerating tenant schemas or common tenant tables
async function gatherTenantData(userId: number) {
  // Simple heuristic: look for common tenant tables in public schema that reference user_id
  const candidateTables = ['orders', 'customer_profiles', 'conversations', 'messages'];
  const out: any = {};
  for (const t of candidateTables) {
    try { out[t] = await knex(t).where({ user_id: userId }).select('*'); } catch (e) { out[t] = []; }
  }
  return out;
}

// GET /api/admin/users/:userId/data-export
router.get('/users/:userId/data-export', dsarLimiter, requirePermission('admin.view'), async (req:any, res) => {
  const userId = Number(req.params.userId);
  if (!userId) return res.status(400).json({ error: 'invalid_user_id' });
  // record audit event
  try { await writeAudit('AUDIT.USER_DATA_EXPORT', { tenantId: req.tenant ? req.tenant.id : null, userId: req.user ? req.user.id : null, metadata: { target_user: userId } }); } catch(e){}

  try {
    // gather data
    const globalData = await gatherGlobalUserData(userId);
    const tenantData = await gatherTenantData(userId);

    const payload = { exported_at: new Date().toISOString(), user_id: userId, global: globalData, tenant_scoped: tenantData };

  // compress JSON payload with gzip and stream to response
  const json = JSON.stringify(payload, null, 2);
  res.setHeader('Content-Type', 'application/gzip');
  res.setHeader('Content-Disposition', `attachment; filename="user-${userId}-data.json.gz"`);
  const gzip = zlib.createGzip();
  gzip.on('error', (err:any) => { console.error('gzip error', err); res.status(500).end(); });
  gzip.pipe(res as any);
  gzip.end(Buffer.from(json, 'utf8'));
  } catch (err:any) {
    console.error('data export failed', err && err.message);
    res.status(500).json({ error: 'export_failed' });
  }
});

export default router;
