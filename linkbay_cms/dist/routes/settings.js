"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const dbMultiTenant_1 = require("../dbMultiTenant");
const crypto_1 = __importDefault(require("crypto"));
const auth_1 = require("../services/auth");
const router = (0, express_1.Router)();
// List API keys (for page rendering)
router.get('/api-keys', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const rows = await k('api_keys').where({ tenant_id: tenant.id }).orderBy('created_at', 'desc').select('id', 'name', 'key_masked', 'created_at');
    res.json(rows);
});
// Create API key: returns partial with full key visible only on creation
router.post('/api-keys', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { name } = req.body;
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const raw = crypto_1.default.randomBytes(32).toString('hex');
    const keyHash = await (0, auth_1.hashPassword)(raw);
    const masked = raw.slice(0, 6) + '...' + raw.slice(-6);
    const [id] = await k('api_keys').insert({ tenant_id: tenant.id, name, key_hash: keyHash, key_masked: masked }).returning('id');
    // return an HTML snippet that includes the full key (only now)
    return res.send(`<div class="p-3 bg-green-50 text-green-800 rounded">Chiave creata: <code class=\"font-mono\">${raw}</code></div><script>htmx.trigger(document.querySelector('#api-keys-list'), 'refresh')</script>`);
});
// Delete API key
router.delete('/api-keys/:id', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const id = Number(req.params.id);
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    await k('api_keys').where({ id, tenant_id: tenant.id }).del();
    // return updated list partial (simpler: return a small message)
    return res.send('<div class="p-2 text-sm text-green-800 bg-green-50 rounded">Chiave eliminata</div><script>htmx.ajax("GET","/api/settings/api-keys?partial=list",{target:document.querySelector("#api-keys-list"),swap:"outerHTML"})</script>');
});
// Webhooks
router.post('/webhooks', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { url, events } = req.body;
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const [id] = await k('webhooks').insert({ tenant_id: tenant.id, url, events }).returning('id');
    // return a new row partial to append
    return res.render('settings/partials/webhook-row', { w: { id, url, events } });
});
router.delete('/webhooks/:id', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const id = Number(req.params.id);
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    await k('webhooks').where({ id, tenant_id: tenant.id }).del();
    return res.send('<div class="p-2 text-sm text-green-800 bg-green-50 rounded">Webhook eliminato</div>');
});
exports.default = router;
