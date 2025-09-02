"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const router = (0, express_1.Router)();
// Serve editor UI - optional language param: /editor/:lang/:pageId
router.get('/:pageId', async (req, res) => {
    // support /editor/:lang/:pageId if first param is lang code
    let pageId = req.params.pageId;
    let lang = 'en';
    const maybeLangMatch = pageId.match(/^([a-z]{2})-(.+)$/);
    if (maybeLangMatch) {
        lang = maybeLangMatch[1];
        pageId = maybeLangMatch[2];
    }
    res.render('editor', { pageId, lang });
});
// API: get page data (tenant middleware should ensure tenant in req)
// GET page content - supports query ?lang=xx
router.get('/api/pages/:pageId', async (req, res) => {
    const { pageId } = req.params;
    const lang = req.query.lang || 'en';
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const row = await (0, db_1.knex)('pages').where({ id: pageId, tenant_id: tenant.id, language: lang }).first();
    if (!row)
        return res.status(404).json({});
    res.json({ content: row.body });
});
// API: save page
router.post('/api/pages/:pageId', async (req, res) => {
    const { pageId } = req.params;
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { html, css, components, language } = req.body;
    const lang = language || 'en';
    const content = JSON.stringify({ html, css, components });
    const existing = await (0, db_1.knex)('pages').where({ id: pageId, tenant_id: tenant.id, language: lang }).first();
    if (existing)
        await (0, db_1.knex)('pages').where({ id: pageId, tenant_id: tenant.id, language: lang }).update({ body: content, updated_at: db_1.knex.fn.now() });
    else
        await (0, db_1.knex)('pages').insert({ tenant_id: tenant.id, slug: `page-${pageId}`, body: content, language: lang });
    res.json({ ok: true });
});
exports.default = router;
