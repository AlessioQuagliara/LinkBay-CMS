"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const router = (0, express_1.Router)();
// List menus for tenant
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const rows = await (0, db_1.knex)('menus').where({ tenant_id: tenant.id }).orderBy('created_at', 'desc');
    res.json(rows);
});
// Create or update menu
router.post('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { id, name, location, items } = req.body;
    const payload = { tenant_id: tenant.id, name, location, items: JSON.stringify(items || []) };
    if (id) {
        await (0, db_1.knex)('menus').where({ id, tenant_id: tenant.id }).update({ ...payload, updated_at: db_1.knex.fn.now() });
        return res.json({ ok: true });
    }
    const [newId] = await (0, db_1.knex)('menus').insert(payload).returning('id');
    res.json({ ok: true, id: newId });
});
// Delete menu
router.delete('/:id', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const id = Number(req.params.id);
    await (0, db_1.knex)('menus').where({ id, tenant_id: tenant.id }).del();
    res.json({ ok: true });
});
// Public: get menu for tenant by location (no auth, tenantResolver must set tenant)
router.get('/public/:location', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const loc = req.params.location;
    const row = await (0, db_1.knex)('menus').where({ tenant_id: tenant.id, location: loc }).first();
    res.json(row || { items: [] });
});
exports.default = router;
