"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const knex_1 = __importDefault(require("knex"));
const dotenv_1 = __importDefault(require("dotenv"));
const auth_1 = require("../services/auth");
dotenv_1.default.config();
const router = (0, express_1.Router)();
// POST /api/auth/tenant-login
// body: { tenant: string, email: string, password: string }
router.post('/tenant-login', async (req, res) => {
    const { tenant, email, password } = req.body;
    if (!tenant || !email || !password)
        return res.status(400).json({ error: 'missing' });
    const knex = (0, knex_1.default)({ client: 'pg', connection: process.env.DATABASE_URL });
    const tenantRow = await knex('tenants').where({ subdomain: tenant }).first();
    if (!tenantRow)
        return res.status(404).json({ error: 'tenant_not_found' });
    const user = await knex('users').where({ tenant_id: tenantRow.id, email }).first();
    if (!user)
        return res.status(401).json({ error: 'invalid' });
    const valid = await (0, auth_1.comparePassword)(password, user.password_hash);
    if (!valid)
        return res.status(401).json({ error: 'invalid' });
    // sign a token containing user id and tenant id; short lived
    const token = (0, auth_1.signAccessToken)({ id: user.id, tenant_id: tenantRow.id, role: user.role }, '10m');
    // redirect to tenant subdomain's callback endpoint with token as query param
    // Build target host using tenant subdomain and APP_URL base domain if present
    const appUrl = process.env.APP_URL || `http://localhost:${process.env.PORT || 3001}`;
    try {
        const url = new URL(appUrl);
        // replace hostname with tenant subdomain while preserving protocol and port
        const host = `${tenant}.${url.hostname}`;
        const port = url.port ? `:${url.port}` : '';
        const target = `${url.protocol}//${host}${port}/auth/callback?token=${encodeURIComponent(token)}`;
        return res.json({ ok: true, redirect: target });
    }
    catch (e) {
        // fallback: assume local host pattern
        const target = `http://${tenant}.localhost:${process.env.PORT || 3001}/auth/callback?token=${encodeURIComponent(token)}`;
        return res.json({ ok: true, redirect: target });
    }
});
// POST /api/auth/provider-redirect
// body: { provider: string, tenant?: string, email?: string }
router.post('/provider-redirect', async (req, res) => {
    const { provider } = req.body;
    let tenant = (req.body && req.body.tenant) || req.query.tenant;
    const email = ((req.body && req.body.email) || req.query.email || '').toString().toLowerCase();
    if (!provider)
        return res.status(400).json({ error: 'provider_required' });
    try {
        const knex = (0, knex_1.default)({ client: 'pg', connection: process.env.DATABASE_URL });
        if (!tenant && email) {
            const user = await knex('users').whereRaw('lower(email) = ?', [email]).first();
            if (user) {
                const t = await knex('tenants').where({ id: user.tenant_id }).first();
                if (t)
                    tenant = t.subdomain;
            }
        }
        if (!tenant)
            return res.status(404).json({ error: 'tenant_not_found' });
        // build tenant host
        const appUrl = process.env.APP_URL || `http://localhost:${process.env.PORT || 3001}`;
        const u = new URL(appUrl);
        const targetHost = `${tenant}.${u.hostname}${u.port ? `:${u.port}` : ''}`;
        // respond with the tenant-scoped provider url (the tenant app will perform redirect)
        return res.json({ ok: true, redirect: `${u.protocol}//${targetHost}/auth/${provider}` });
    }
    catch (e) {
        return res.status(500).json({ error: 'internal' });
    }
});
exports.default = router;
