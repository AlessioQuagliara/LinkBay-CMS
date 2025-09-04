import { Router } from 'express';
import knexInit from 'knex';
import dotenv from 'dotenv';
import { comparePassword, signAccessToken } from '../services/auth';
dotenv.config();

const router = Router();

// POST /api/auth/tenant-login
// body: { tenant: string, email: string, password: string }
router.post('/tenant-login', async (req, res) => {
  const { tenant, email, password } = req.body as any;
  if (!tenant || !email || !password) return res.status(400).json({ error: 'missing' });
    const knex = knexInit({ client: 'pg', connection: process.env.DATABASE_URL });
  const tenantRow = await knex('tenants').where({ subdomain: tenant }).first();
  if (!tenantRow) return res.status(404).json({ error: 'tenant_not_found' });
  const user = await knex('users').where({ tenant_id: tenantRow.id, email }).first();
  if (!user) return res.status(401).json({ error: 'invalid' });
  const valid = await comparePassword(password, user.password_hash);
  if (!valid) return res.status(401).json({ error: 'invalid' });

  // sign a token containing user id and tenant id; short lived
  const token = signAccessToken({ id: user.id, tenant_id: tenantRow.id, role: user.role }, '10m');

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
  } catch (e) {
    // fallback: assume local host pattern
    const target = `http://${tenant}.localhost:${process.env.PORT || 3001}/auth/callback?token=${encodeURIComponent(token)}`;
    return res.json({ ok: true, redirect: target });
  }
});

// POST /api/auth/provider-redirect
// body: { provider: string, tenant?: string, email?: string }
router.post('/provider-redirect', async (req, res) => {
  const { provider } = req.body as any;
  let tenant = (req.body && req.body.tenant) || req.query.tenant;
  const email = ((req.body && req.body.email) || req.query.email || '').toString().toLowerCase();
  if (!provider) return res.status(400).json({ error: 'provider_required' });
  try {
    const knex = knexInit({ client: 'pg', connection: process.env.DATABASE_URL });
    if (!tenant && email) {
      const user = await knex('users').whereRaw('lower(email) = ?', [email]).first();
      if (user) {
        const t = await knex('tenants').where({ id: user.tenant_id }).first();
        if (t) tenant = t.subdomain;
      }
    }
    if (!tenant) return res.status(404).json({ error: 'tenant_not_found' });
    // build tenant host
    const appUrl = process.env.APP_URL || `http://localhost:${process.env.PORT || 3001}`;
    const u = new URL(appUrl);
    const targetHost = `${tenant}.${u.hostname}${u.port ? `:${u.port}` : ''}`;
    // respond with the tenant-scoped provider url (the tenant app will perform redirect)
    return res.json({ ok: true, redirect: `${u.protocol}//${targetHost}/auth/${provider}` });
  } catch (e) {
    return res.status(500).json({ error: 'internal' });
  }
});

export default router;
