"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const audit_1 = require("../middleware/audit");
const zlib_1 = __importDefault(require("zlib"));
const router = (0, express_1.Router)();
// strict rate limiter for DSAR endpoints (per admin user)
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const dsarLimiter = (0, express_rate_limit_1.default)({ windowMs: 60 * 60 * 1000, max: 5, keyGenerator: (req) => `dsar_user_${req.user ? req.user.id : req.ip}`, standardHeaders: true, legacyHeaders: false });
// Helper: gather rows for a given user across common tables
async function gatherGlobalUserData(userId) {
    const out = {};
    const tables = ['users', 'orders', 'invoices', 'audit_logs'];
    for (const t of tables) {
        try {
            out[t] = await (0, db_1.knex)(t).where({ user_id: userId }).select('*');
        }
        catch (e) {
            out[t] = [];
        }
    }
    return out;
}
// Helper: gather tenant-scoped data by enumerating tenant schemas or common tenant tables
async function gatherTenantData(userId) {
    // Simple heuristic: look for common tenant tables in public schema that reference user_id
    const candidateTables = ['orders', 'customer_profiles', 'conversations', 'messages'];
    const out = {};
    for (const t of candidateTables) {
        try {
            out[t] = await (0, db_1.knex)(t).where({ user_id: userId }).select('*');
        }
        catch (e) {
            out[t] = [];
        }
    }
    return out;
}
// GET /api/admin/users/:userId/data-export
router.get('/users/:userId/data-export', dsarLimiter, (0, permissions_1.requirePermission)('admin.view'), async (req, res) => {
    const userId = Number(req.params.userId);
    if (!userId)
        return res.status(400).json({ error: 'invalid_user_id' });
    // record audit event
    try {
        await (0, audit_1.writeAudit)('AUDIT.USER_DATA_EXPORT', { tenantId: req.tenant ? req.tenant.id : null, userId: req.user ? req.user.id : null, metadata: { target_user: userId } });
    }
    catch (e) { }
    try {
        // gather data
        const globalData = await gatherGlobalUserData(userId);
        const tenantData = await gatherTenantData(userId);
        const payload = { exported_at: new Date().toISOString(), user_id: userId, global: globalData, tenant_scoped: tenantData };
        // compress JSON payload with gzip and stream to response
        const json = JSON.stringify(payload, null, 2);
        res.setHeader('Content-Type', 'application/gzip');
        res.setHeader('Content-Disposition', `attachment; filename="user-${userId}-data.json.gz"`);
        const gzip = zlib_1.default.createGzip();
        gzip.on('error', (err) => { console.error('gzip error', err); res.status(500).end(); });
        gzip.pipe(res);
        gzip.end(Buffer.from(json, 'utf8'));
    }
    catch (err) {
        console.error('data export failed', err && err.message);
        res.status(500).json({ error: 'export_failed' });
    }
});
exports.default = router;
