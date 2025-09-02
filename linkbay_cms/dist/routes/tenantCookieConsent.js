"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const tenantResolver_1 = require("../middleware/tenantResolver");
const router = (0, express_1.Router)();
router.use(tenantResolver_1.tenantResolver);
// GET current config for tenant
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    try {
        const row = await (0, db_1.knex)('tenant_cookie_consent').where({ tenant_id: tenant.id }).first();
        res.json({ success: true, config: row || null });
    }
    catch (e) {
        res.status(500).json({ error: 'server_error' });
    }
});
// POST update config for tenant
router.post('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    const { banner_text, necessary_cookies, analytics_cookies, marketing_cookies, enabled } = req.body;
    try {
        const existing = await (0, db_1.knex)('tenant_cookie_consent').where({ tenant_id: tenant.id }).first();
        if (existing) {
            await (0, db_1.knex)('tenant_cookie_consent').where({ tenant_id: tenant.id }).update({ banner_text, necessary_cookies, analytics_cookies, marketing_cookies, enabled, updated_at: new Date() });
        }
        else {
            await (0, db_1.knex)('tenant_cookie_consent').insert({ tenant_id: tenant.id, banner_text, necessary_cookies, analytics_cookies, marketing_cookies, enabled });
        }
        res.json({ success: true });
    }
    catch (e) {
        console.error('save cookie config failed', e);
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
