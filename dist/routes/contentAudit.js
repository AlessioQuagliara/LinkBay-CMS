"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const router = (0, express_1.Router)();
router.use((0, permissions_1.requirePermission)('admin.view'));
// list page versions
router.get('/pages/:id/versions', async (req, res) => {
    const id = Number(req.params.id);
    try {
        const rows = await (0, db_1.knex)('pages_audit').where({ page_id: id }).orderBy('version', 'desc').select('*');
        res.json({ success: true, versions: rows });
    }
    catch (e) {
        res.status(500).json({ error: 'server_error' });
    }
});
// rollback page to a specific version
router.post('/pages/:id/rollback/:version', async (req, res) => {
    const id = Number(req.params.id);
    const version = Number(req.params.version);
    try {
        const snap = await (0, db_1.knex)('pages_audit').where({ page_id: id, version }).first();
        if (!snap)
            return res.status(404).json({ error: 'not_found' });
        await (0, db_1.knex)('pages').where({ id }).update({ name: snap.name, content_json: snap.content_json, content_html: snap.content_html, slug: snap.slug, updated_at: new Date() });
        res.json({ success: true });
    }
    catch (e) {
        res.status(500).json({ error: 'server_error' });
    }
});
// list product versions
router.get('/products/:id/versions', async (req, res) => {
    const id = Number(req.params.id);
    try {
        const rows = await (0, db_1.knex)('products_audit').where({ product_id: id }).orderBy('version', 'desc').select('*');
        res.json({ success: true, versions: rows });
    }
    catch (e) {
        res.status(500).json({ error: 'server_error' });
    }
});
// rollback product (replaces current row with payload JSON)
router.post('/products/:id/rollback/:version', async (req, res) => {
    const id = Number(req.params.id);
    const version = Number(req.params.version);
    try {
        const snap = await (0, db_1.knex)('products_audit').where({ product_id: id, version }).first();
        if (!snap)
            return res.status(404).json({ error: 'not_found' });
        const payload = snap.payload ? JSON.parse(snap.payload) : null;
        if (!payload)
            return res.status(500).json({ error: 'invalid_snapshot' });
        await (0, db_1.knex)('products').where({ id }).update({ ...payload, updated_at: new Date() });
        res.json({ success: true });
    }
    catch (e) {
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
