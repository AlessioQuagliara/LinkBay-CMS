"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const audit_1 = require("../middleware/audit");
const router = (0, express_1.Router)();
router.use((0, permissions_1.requirePermission)('admin.view'));
// POST /api/admin/users/:userId/anonymize
router.post('/users/:userId/anonymize', async (req, res) => {
    const targetId = Number(req.params.userId);
    if (!targetId)
        return res.status(400).json({ error: 'invalid_user_id' });
    try {
        // fetch user (global table)
        const user = await (0, db_1.knex)('users').where({ id: targetId }).first();
        if (!user)
            return res.status(404).json({ error: 'not_found' });
        // perform anonymization - best-effort within a transaction
        await db_1.knex.transaction(async (trx) => {
            // update main users row
            const anonEmail = `user_${targetId}@deleted.local`;
            await trx('users').where({ id: targetId }).update({ email: anonEmail, name: '[Redacted]', address: '[Redacted]', anonymized_at: new Date() });
            // also anonymize related tenant tables that commonly store PII
            const tenantTables = ['customer_profiles', 'orders', 'invoices'];
            for (const t of tenantTables) {
                try {
                    const cols = await trx.raw(`SELECT column_name FROM information_schema.columns WHERE table_name = ?`, [t]);
                    const colNames = cols && cols.rows ? cols.rows.map((r) => r.column_name) : [];
                    const updates = {};
                    if (colNames.includes('email'))
                        updates.email = anonEmail;
                    if (colNames.includes('name'))
                        updates.name = '[Redacted]';
                    if (colNames.includes('address'))
                        updates.address = '[Redacted]';
                    if (Object.keys(updates).length)
                        await trx(t).where({ user_id: targetId }).update(updates);
                }
                catch (e) { /* ignore missing tables */ }
            }
        });
        try {
            await (0, audit_1.writeAudit)('AUDIT.USER_ANONYMIZED', { tenantId: req.tenant ? req.tenant.id : null, userId: req.user ? req.user.id : null, metadata: { target_user: targetId } });
        }
        catch (e) { }
        res.json({ success: true });
    }
    catch (err) {
        console.error('anonymize failed', err && err.message);
        res.status(500).json({ error: 'anonymize_failed' });
    }
});
exports.default = router;
