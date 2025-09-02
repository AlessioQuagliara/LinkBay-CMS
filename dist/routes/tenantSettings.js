"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const audit_1 = require("../middleware/audit");
function sanitizeTrackingScript(input) {
    if (!input || typeof input !== 'string')
        return null;
    const lowered = input.toLowerCase();
    // allowlist simple checks for common providers
    const allowPatterns = ['googletagmanager.com', 'gtag(', 'google-analytics.com', 'connect.facebook.net', 'fbq(', 'facebook.com/tr', 'adsbygoogle', 'googlesyndication'];
    const ok = allowPatterns.some(p => lowered.includes(p));
    if (!ok)
        return null;
    // minimal sanitize: strip out <script> tags with inline event handlers by removing 'onerror=' etc
    // Note: this is a basic heuristic; for production use a robust sanitizer like DOMPurify on the server or store scripts as-is but restrict access.
    return input.replace(/on\w+\s*=\s*\"[^\"]*\"/gi, '').replace(/on\w+\s*=\s*\'[^\']*\'/gi, '');
}
const router = (0, express_1.Router)();
// GET /api/tenant/settings
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const row = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
    res.json(row || {});
});
// PUT /api/tenant/settings
router.put('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { primary_color, secondary_color, logo_url, favicon_url, css_overrides, default_theme } = req.body;
    const exists = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
    const payload = { primary_color, secondary_color, logo_url, favicon_url, css_overrides, default_theme };
    if (exists) {
        const before = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
        await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).update({ ...payload, updated_at: db_1.knex.fn.now() });
        try {
            await (0, audit_1.auditChange)('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: req.user ? req.user.id : undefined, oldValue: before, newValue: { ...before, ...payload } });
        }
        catch (e) { }
    }
    else {
        await (0, db_1.knex)('tenant_settings').insert({ tenant_id: tenant.id, ...payload });
        try {
            await (0, audit_1.auditChange)('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: req.user ? req.user.id : undefined, oldValue: null, newValue: payload });
        }
        catch (e) { }
    }
    const row = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
    res.json(row);
});
// PUT /api/tenant/tracking-scripts
router.put('/tracking-scripts', (0, permissions_1.requirePermission)('settings.manage'), async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { tracking_scripts } = req.body;
    const sanitized = sanitizeTrackingScript(tracking_scripts);
    if (tracking_scripts && !sanitized)
        return res.status(400).json({ error: 'invalid_tracking_scripts' });
    const exists = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
    if (exists) {
        const before = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
        await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).update({ tracking_scripts: sanitized, updated_at: db_1.knex.fn.now() });
        try {
            await (0, audit_1.auditChange)('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: req.user ? req.user.id : undefined, oldValue: before, newValue: { ...before, tracking_scripts: sanitized } });
        }
        catch (e) { }
    }
    else {
        await (0, db_1.knex)('tenant_settings').insert({ tenant_id: tenant.id, tracking_scripts: sanitized });
        try {
            await (0, audit_1.auditChange)('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: req.user ? req.user.id : undefined, oldValue: null, newValue: { tracking_scripts: sanitized } });
        }
        catch (e) { }
    }
    const row = await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first();
    res.json(row);
});
exports.default = router;
