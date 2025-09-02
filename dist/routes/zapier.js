"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const crypto_1 = __importDefault(require("crypto"));
const router = (0, express_1.Router)();
// OAuth authorize (Zapier will redirect users here to connect their tenant)
router.get('/oauth/authorize', async (req, res) => {
    // params: client_id, redirect_uri, state, scope
    const { client_id, redirect_uri, state, scope } = req.query;
    // For simplicity assume admin is logged in and tenant is available via req.tenant
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).send('tenant_required');
    const code = crypto_1.default.randomBytes(24).toString('hex');
    await (0, db_1.knex)('zapier_oauth_codes').insert({ code, tenant_id: tenant.id, client_id, expires_at: new Date(Date.now() + 600000) });
    const redirect = `${redirect_uri}?code=${code}&state=${encodeURIComponent(state || '')}`;
    res.redirect(redirect);
});
// OAuth token exchange
router.post('/oauth/token', async (req, res) => {
    const { code, client_id, grant_type } = req.body;
    if (grant_type !== 'authorization_code')
        return res.status(400).json({ error: 'unsupported_grant' });
    const row = await (0, db_1.knex)('zapier_oauth_codes').where({ code, client_id }).first();
    if (!row || new Date(row.expires_at) < new Date())
        return res.status(400).json({ error: 'invalid_code' });
    const access = crypto_1.default.randomBytes(32).toString('hex');
    // requested scopes can be provided when exchanging code; fallback to all scopes
    const requestedScopes = req.body.scope ? (Array.isArray(req.body.scope) ? req.body.scope : String(req.body.scope).split(' ')) : ['*'];
    await (0, db_1.knex)('zapier_oauth_tokens').insert({ access_token: access, tenant_id: row.tenant_id, client_id, scopes: JSON.stringify(requestedScopes), expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30) });
    res.json({ access_token: access, token_type: 'bearer', expires_in: 60 * 60 * 24 * 30 });
});
// Middleware to check Zapier token and attach tenant
async function requireZapierToken(req, res, next) {
    const auth = req.headers.authorization || '';
    if (!auth.startsWith('Bearer '))
        return res.status(401).json({ error: 'token_required' });
    const token = auth.slice(7);
    const row = await (0, db_1.knex)('zapier_oauth_tokens').where({ access_token: token }).first();
    if (!row)
        return res.status(401).json({ error: 'invalid_token' });
    try {
        req.zapierScopes = row.scopes ? (Array.isArray(row.scopes) ? row.scopes : JSON.parse(row.scopes)) : [];
    }
    catch (e) {
        req.zapierScopes = row.scopes || [];
    }
    req.tenant = { id: row.tenant_id };
    next();
}
function requireZapierScope(scope) {
    return (req, res, next) => {
        const scopes = req.zapierScopes || [];
        if (scopes.includes(scope) || scopes.includes('*'))
            return next();
        return res.status(403).json({ error: 'insufficient_scope' });
    };
}
// Discovery: list triggers/actions
router.get('/triggers', (req, res) => {
    res.json({ triggers: [{ key: 'new_order', name: 'New Order' }], actions: [{ key: 'create_product', name: 'Create Product' }] });
});
// Trigger endpoint example: returns recent orders (Zapier polls this)
router.get('/triggers/new-order', requireZapierToken, requireZapierScope('orders:read'), async (req, res) => {
    const tenantId = req.tenant.id;
    const orders = await (0, db_1.knex)('orders').where({ tenant_id: tenantId }).orderBy('created_at', 'desc').limit(50);
    res.json(orders);
});
// Action endpoint: create product
router.post('/actions/create-product', requireZapierToken, requireZapierScope('products:write'), async (req, res) => {
    const tenantId = req.tenant.id;
    const { name, price_cents, description } = req.body;
    if (!name || !price_cents)
        return res.status(400).json({ error: 'name_and_price_required' });
    const [id] = await (0, db_1.knex)('products').insert({ tenant_id: tenantId, name, price_cents, description, created_at: new Date() }).returning('id');
    res.json({ id });
});
exports.default = router;
