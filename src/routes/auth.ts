import { Router } from 'express';
import { knex as createKnex } from 'knex';
import dotenv from 'dotenv';
dotenv.config();
import { hashPassword, comparePassword, signAccessToken, signRefreshToken } from '../services/auth';
import { sendMail } from '../services/mailer';
import { logAuditEvent } from '../middleware/audit';
import { authLimiter, loginBackoff } from '../middleware/rateLimiters';
import eventBus from '../lib/eventBus';
import { verifyToken } from '../services/auth';

const router = Router();

const isHx = (req: any) => !!req.get('HX-Request');

// Render login page
router.get('/login', async (req:any, res) => {
  res.render('auth/login', { title: 'Login', tenant: (req as any).tenant, flash: (req as any).flash || {} });
});

// Render register page
router.get('/register', async (req:any, res) => {
  res.render('auth/register', { title: 'Register', tenant: (req as any).tenant, flash: (req as any).flash || {} });
});

// Register - create user within tenant context (tenantResolver should attach tenant)
router.post('/register', logAuditEvent('user.register', (req)=>({ email: req.body.email })), async (req: any, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) {
    if (isHx(req)) return res.status(400).render('partials/form-errors', { errors: { tenant: 'Tenant required' } });
    return res.status(400).json({ error: 'tenant_required' });
  }
  const { email, password, role } = req.body;
  const errors: any = {};
  if (!email) errors.email = 'Email is required';
  if (!password) errors.password = 'Password is required';
  if (Object.keys(errors).length) {
    if (isHx(req)) return res.status(400).render('partials/form-errors', { errors });
    return res.status(400).json({ error: 'validation', errors });
  }
  const knex = createKnex({ client: 'pg', connection: process.env.DATABASE_URL });
  const existing = await knex('users').where({ tenant_id: tenant.id, email }).first();
  if (existing) {
    if (isHx(req)) return res.status(400).render('partials/form-errors', { errors: { email: 'Email already registered' } });
    return res.status(400).json({ error: 'exists' });
  }
  const hash = await hashPassword(password);
  const [id] = await knex('users').insert({ tenant_id: tenant.id, email, password_hash: hash, role }).returning('id');
  // send verification mail (stub)
  sendMail({ to: email, subject: 'Verify', text: 'verify link' }).catch(()=>{});
  if (isHx(req)) {
    res.set('HX-Redirect', '/dashboard');
    return res.status(200).send('');
  }
  res.json({ ok: true, id });
});

// Login
router.post('/login', authLimiter(), loginBackoff(), logAuditEvent('user.login', (req)=>({ email: req.body.email })), async (req:any, res) => {
  const { email, password } = req.body;
  const knex = createKnex({ client: 'pg', connection: process.env.DATABASE_URL });
  const user = await knex('users').where({ email }).first();
  if (!user) {
    if (isHx(req)) return res.status(401).render('partials/form-errors', { errors: { login: 'Invalid email or password' } });
    return res.status(401).json({ error: 'invalid' });
  }
  const valid = await comparePassword(password, user.password_hash);
  if (!valid) {
    if (isHx(req)) return res.status(401).render('partials/form-errors', { errors: { login: 'Invalid email or password' } });
    return res.status(401).json({ error: 'invalid' });
  }
  const access = signAccessToken({ id: user.id, tenant_id: user.tenant_id, role: user.role });
  const refresh = signRefreshToken({ id: user.id });
  await knex('refresh_tokens').insert({ user_id: user.id, token: refresh, expires_at: new Date(Date.now() + 1000*60*60*24*30) });
  // load user preferences to return to client
  const prefRows = await knex('user_preferences').where({ user_id: user.id }).select('key','value');
  const preferences: Record<string, any> = {};
  prefRows.forEach(r=>{ try { preferences[r.key] = JSON.parse(r.value); } catch(e){ preferences[r.key] = r.value; } });
  // emit user logged in event
  try { eventBus.emit({ type: 'UserLoggedIn', user_id: user.id, tenant_id: user.tenant_id || null, ip: req.ip, timestamp: new Date().toISOString() }); } catch(e){}
  if (isHx(req)) {
    res.set('HX-Redirect', '/dashboard');
    return res.status(200).send('');
  }
  res.json({ ok: true, token: access, refresh, preferences });
});

// Forgot password (example endpoint) - apply auth limiter/backoff
router.post('/forgot-password', authLimiter(), loginBackoff(), logAuditEvent('user.forgot_password', (req)=>({ email: req.body.email })), async (req, res) => {
  const { email } = req.body;
  // simple stub: send reset email
  sendMail({ to: email, subject: 'Reset', text: 'reset link' }).catch(()=>{});
  res.json({ ok: true });
});

// Refresh
router.post('/refresh', async (req, res) => {
  const { refresh } = req.body;
  const knex = createKnex({ client: 'pg', connection: process.env.DATABASE_URL });
  try {
    const payload: any = (await import('jsonwebtoken')).verify(refresh, process.env.SESSION_SECRET || 'devsecret');
    const record = await knex('refresh_tokens').where({ token: refresh, user_id: payload.id }).first();
    if (!record) return res.status(401).json({ error: 'invalid' });
    const user = await knex('users').where({ id: payload.id }).first();
    const access = signAccessToken({ id: user.id, tenant_id: user.tenant_id, role: user.role });
    res.json({ ok: true, token: access });
  } catch (err:any) {
    res.status(401).json({ error: 'invalid', message: err && err.message });
  }
});

// Logout
router.post('/logout', logAuditEvent('user.logout', (req)=>({ user_id: (req as any).user && (req as any).user.id })), async (req, res) => {
  const { refresh } = req.body;
  const knex = createKnex({ client: 'pg', connection: process.env.DATABASE_URL });
  await knex('refresh_tokens').where({ token: refresh }).del();
  res.json({ ok: true });
});

// Callback for cross-domain login — tenant subdomain should receive a token from public domain
router.get('/callback', async (req, res) => {
  const token = (req.query.token || req.query.t || '').toString();
  if (!token) return res.status(400).send('missing token');
  try {
    const payload: any = verifyToken(token as string) as any;
    // set cookie scoped to current hostname (tenant subdomain). Use httpOnly and secure when in production.
    const cookieOptions: any = { httpOnly: true, maxAge: 1000*60*60*24*7 };
    if (process.env.NODE_ENV === 'production') cookieOptions.secure = true;
    // cookie name: access_token
    res.cookie('access_token', token, cookieOptions);
    // redirect to dashboard
    return res.redirect('/dashboard');
  } catch (e:any) {
    return res.status(400).send('invalid token');
  }
});

export default router;

