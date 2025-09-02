"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const router = (0, express_1.Router)();
// list public integrations
router.get('/', async (req, res) => {
    const list = await (0, db_1.knex)('public_integrations').where({ is_active: true }).select('*');
    res.json(list);
});
// install for tenant: saves config into tenant_integrations
router.post('/install/:id', async (req, res) => {
    const tid = Number(req.params.id);
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).json({ error: 'tenant_required' });
    const integration = await (0, db_1.knex)('public_integrations').where({ id: tid }).first();
    if (!integration)
        return res.status(404).json({ error: 'not_found' });
    const cfg = req.body.config || {};
    const [id] = await (0, db_1.knex)('tenant_integrations').insert({ tenant_id: tenant.id, provider: integration.name.toLowerCase(), config: JSON.stringify(cfg), is_active: true, created_at: new Date() }).returning('id');
    // optional: if integration requires auto webhook registration, register hooks (not implemented automatically here)
    res.json({ ok: true, id });
});
// UI render for configuration based on config_schema (simple dynamic form)
router.get('/configure/:id', async (req, res) => {
    const id = Number(req.params.id);
    const integration = await (0, db_1.knex)('public_integrations').where({ id }).first();
    if (!integration)
        return res.status(404).send('not found');
    const schema = integration.config_schema || [];
    res.render('integration_configure', { integration, schema });
});
exports.default = router;
