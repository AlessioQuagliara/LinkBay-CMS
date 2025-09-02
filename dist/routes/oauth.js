"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const node_fetch_1 = __importDefault(require("node-fetch"));
const auth_1 = require("../services/auth");
const auth_2 = require("../services/auth");
const eventBus_1 = __importDefault(require("../lib/eventBus"));
const router = (0, express_1.Router)();
// Helper: get provider config for tenant
async function getProvider(tenantId, providerName) {
    return (0, db_1.knex)('tenant_oauth_providers').where({ tenant_id: tenantId, provider_name: providerName }).first();
}
// Redirect to provider
router.get('/:provider', async (req, res) => {
    const provider = req.params.provider;
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).send('tenant_required');
    const cfg = await getProvider(tenant.id, provider);
    if (!cfg)
        return res.status(404).send('provider_not_configured');
    const redirectUri = `${process.env.APP_URL || 'http://localhost:3001'}/auth/${provider}/callback`;
    if (provider === 'google') {
        const scope = cfg.scopes || 'openid email profile';
        const url = `https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id=${encodeURIComponent(cfg.client_id)}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}&access_type=offline&prompt=consent`;
        return res.redirect(url);
    }
    if (provider === 'github') {
        const scope = cfg.scopes || 'user:email';
        const url = `https://github.com/login/oauth/authorize?client_id=${encodeURIComponent(cfg.client_id)}&redirect_uri=${encodeURIComponent(redirectUri)}&scope=${encodeURIComponent(scope)}`;
        return res.redirect(url);
    }
    res.status(400).send('unsupported_provider');
});
// Callback
router.get('/:provider/callback', async (req, res) => {
    const provider = req.params.provider;
    const code = req.query.code;
    const tenant = req.tenant;
    if (!tenant)
        return res.status(400).send('tenant_required');
    const cfg = await getProvider(tenant.id, provider);
    if (!cfg)
        return res.status(404).send('provider_not_configured');
    try {
        let profile = null;
        if (provider === 'google') {
            // exchange code for token
            const tokenRes = await (0, node_fetch_1.default)('https://oauth2.googleapis.com/token', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: `code=${encodeURIComponent(code)}&client_id=${encodeURIComponent(cfg.client_id)}&client_secret=${encodeURIComponent(cfg.client_secret)}&redirect_uri=${encodeURIComponent(process.env.APP_URL + '/auth/google/callback')}&grant_type=authorization_code` });
            const tokenJson = await tokenRes.json();
            const userRes = await (0, node_fetch_1.default)('https://www.googleapis.com/oauth2/v2/userinfo', { headers: { Authorization: `Bearer ${tokenJson.access_token}` } });
            profile = await userRes.json();
            // profile.email, profile.name, profile.id
        }
        else if (provider === 'github') {
            const tokenRes = await (0, node_fetch_1.default)('https://github.com/login/oauth/access_token', { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/json' }, body: JSON.stringify({ client_id: cfg.client_id, client_secret: cfg.client_secret, code, redirect_uri: process.env.APP_URL + '/auth/github/callback' }) });
            const tokenJson = await tokenRes.json();
            const userRes = await (0, node_fetch_1.default)('https://api.github.com/user', { headers: { Authorization: `token ${tokenJson.access_token}`, Accept: 'application/vnd.github.v3+json' } });
            const user = await userRes.json();
            // get primary email
            let email = null;
            const emailsRes = await (0, node_fetch_1.default)('https://api.github.com/user/emails', { headers: { Authorization: `token ${tokenJson.access_token}`, Accept: 'application/vnd.github.v3+json' } });
            const emails = await emailsRes.json();
            if (Array.isArray(emails)) {
                const primary = emails.find((e) => e.primary) || emails[0];
                email = primary && primary.email;
            }
            profile = { id: user.id, name: user.name || user.login, email };
        }
        if (!profile || !profile.email)
            return res.status(400).send('no_email');
        // find or create user
        let user = await (0, db_1.knex)('users').where({ email: profile.email, tenant_id: tenant.id }).first();
        if (!user) {
            const pwd = Math.random().toString(36).slice(2);
            const pwdHash = await (0, auth_2.hashPassword)(pwd);
            const [id] = await (0, db_1.knex)('users').insert({ tenant_id: tenant.id, email: profile.email, password_hash: pwdHash, role: 'user', created_at: new Date() }).returning('id');
            user = await (0, db_1.knex)('users').where({ id }).first();
        }
        // create JWTs
        const access = (0, auth_1.signAccessToken)({ id: user.id, tenant_id: user.tenant_id, role: user.role });
        const refresh = (0, auth_1.signRefreshToken)({ id: user.id });
        await (0, db_1.knex)('refresh_tokens').insert({ user_id: user.id, token: refresh, expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30) });
        // emit login event
        try {
            eventBus_1.default.emit({ type: 'UserLoggedIn', user_id: user.id, tenant_id: user.tenant_id || null, ip: req.ip, timestamp: new Date().toISOString() });
        }
        catch (e) { }
        // return tokens (for browser we can set cookie; here just show JSON)
        res.json({ ok: true, token: access, refresh });
    }
    catch (err) {
        console.error('oauth callback error', err);
        res.status(500).json({ error: 'oauth_failed', message: err && err.message });
    }
});
exports.default = router;
