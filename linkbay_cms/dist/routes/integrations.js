"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const node_fetch_1 = __importDefault(require("node-fetch"));
const router = (0, express_1.Router)();
// Start HubSpot OAuth flow
router.get('/hubspot/connect', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).send('tenant_required');
    const clientId = process.env.HUBSPOT_CLIENT_ID || '';
    if (!clientId)
        return res.status(500).send('hubspot_client_not_configured');
    const redirect = `${process.env.APP_URL || 'http://localhost:3001'}/integrations/hubspot/callback`;
    const scope = 'contacts content';
    const url = `https://app.hubspot.com/oauth/authorize?client_id=${encodeURIComponent(clientId)}&scope=${encodeURIComponent(scope)}&redirect_uri=${encodeURIComponent(redirect)}`;
    res.redirect(url);
});
// Callback
router.get('/hubspot/callback', async (req, res) => {
    const code = req.query.code;
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).send('tenant_required');
    try {
        const tokenRes = await (0, node_fetch_1.default)('https://api.hubapi.com/oauth/v1/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: `grant_type=authorization_code&client_id=${encodeURIComponent(process.env.HUBSPOT_CLIENT_ID || '')}&client_secret=${encodeURIComponent(process.env.HUBSPOT_CLIENT_SECRET || '')}&redirect_uri=${encodeURIComponent(process.env.APP_URL + '/integrations/hubspot/callback')}&code=${encodeURIComponent(code)}` });
        const tokenJson = await tokenRes.json();
        // save integration
        const [id] = await (0, db_1.knex)('tenant_integrations').insert({ tenant_id: tenant.id, provider: 'hubspot', access_token: tokenJson.access_token, refresh_token: tokenJson.refresh_token, expires_at: tokenJson.expires_in ? new Date(Date.now() + tokenJson.expires_in * 1000) : null, is_active: true, created_at: new Date() }).returning('id');
        res.render('integration_connected', { provider: 'hubspot', id });
    }
    catch (err) {
        console.error('hubspot callback', err);
        res.status(500).send('oauth_failed');
    }
});
// Mapping CRUD
router.get('/:integrationId/mapping', async (req, res) => {
    const id = Number(req.params.integrationId);
    const map = await (0, db_1.knex)('integration_mappings').where({ integration_id: id }).first();
    res.json(map);
});
router.post('/:integrationId/mapping', async (req, res) => {
    const id = Number(req.params.integrationId);
    const body = req.body || {};
    const exists = await (0, db_1.knex)('integration_mappings').where({ integration_id: id }).first();
    if (exists) {
        await (0, db_1.knex)('integration_mappings').where({ integration_id: id }).update({ mappings: JSON.stringify(body), updated_at: new Date() });
    }
    else {
        await (0, db_1.knex)('integration_mappings').insert({ integration_id: id, entity: body.entity || 'contact', mappings: JSON.stringify(body.mappings || {}), created_at: new Date() });
    }
    res.json({ ok: true });
});
exports.default = router;
