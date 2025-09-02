"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const knex_1 = require("knex");
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const auth_1 = require("../services/auth");
const mailer_1 = require("../services/mailer");
const audit_1 = require("../middleware/audit");
const rateLimiters_1 = require("../middleware/rateLimiters");
const eventBus_1 = __importDefault(require("../lib/eventBus"));
const auth_2 = require("../services/auth");
const router = (0, express_1.Router)();
const isHx = (req) => !!req.get('HX-Request');
// Render login page
router.get('/login', async (req, res) => {
    res.render('auth/login', { title: 'Login', tenant: req.tenant, flash: req.flash || {} });
});
// Render register page
router.get('/register', async (req, res) => {
    res.render('auth/register', { title: 'Register', tenant: req.tenant, flash: req.flash || {} });
});
// Register - create user within tenant context (tenantResolver should attach tenant)
router.post('/register', (0, audit_1.logAuditEvent)('user.register', (req) => ({ email: req.body.email })), async (req, res) => {
    const tenant = req.tenant;
    if (!tenant) {
        if (isHx(req))
            return res.status(400).render('partials/form-errors', { errors: { tenant: 'Tenant required' } });
        return res.status(400).json({ error: 'tenant_required' });
    }
    const { email, password, role } = req.body;
    const errors = {};
    if (!email)
        errors.email = 'Email is required';
    if (!password)
        errors.password = 'Password is required';
    if (Object.keys(errors).length) {
        if (isHx(req))
            return res.status(400).render('partials/form-errors', { errors });
        return res.status(400).json({ error: 'validation', errors });
    }
    const knex = (0, knex_1.knex)({ client: 'pg', connection: process.env.DATABASE_URL });
    const existing = await knex('users').where({ tenant_id: tenant.id, email }).first();
    if (existing) {
        if (isHx(req))
            return res.status(400).render('partials/form-errors', { errors: { email: 'Email already registered' } });
        return res.status(400).json({ error: 'exists' });
    }
    const hash = await (0, auth_1.hashPassword)(password);
    const [id] = await knex('users').insert({ tenant_id: tenant.id, email, password_hash: hash, role }).returning('id');
    // send verification mail (stub)
    (0, mailer_1.sendMail)({ to: email, subject: 'Verify', text: 'verify link' }).catch(() => { });
    if (isHx(req)) {
        res.set('HX-Redirect', '/dashboard');
        return res.status(200).send('');
    }
    res.json({ ok: true, id });
});
// Login
router.post('/login', (0, rateLimiters_1.authLimiter)(), (0, rateLimiters_1.loginBackoff)(), (0, audit_1.logAuditEvent)('user.login', (req) => ({ email: req.body.email })), async (req, res) => {
    const { email, password } = req.body;
    const knex = (0, knex_1.knex)({ client: 'pg', connection: process.env.DATABASE_URL });
    const user = await knex('users').where({ email }).first();
    if (!user) {
        if (isHx(req))
            return res.status(401).render('partials/form-errors', { errors: { login: 'Invalid email or password' } });
        return res.status(401).json({ error: 'invalid' });
    }
    const valid = await (0, auth_1.comparePassword)(password, user.password_hash);
    if (!valid) {
        if (isHx(req))
            return res.status(401).render('partials/form-errors', { errors: { login: 'Invalid email or password' } });
        return res.status(401).json({ error: 'invalid' });
    }
    const access = (0, auth_1.signAccessToken)({ id: user.id, tenant_id: user.tenant_id, role: user.role });
    const refresh = (0, auth_1.signRefreshToken)({ id: user.id });
    await knex('refresh_tokens').insert({ user_id: user.id, token: refresh, expires_at: new Date(Date.now() + 1000 * 60 * 60 * 24 * 30) });
    // load user preferences to return to client
    const prefRows = await knex('user_preferences').where({ user_id: user.id }).select('key', 'value');
    const preferences = {};
    prefRows.forEach(r => { try {
        preferences[r.key] = JSON.parse(r.value);
    }
    catch (e) {
        preferences[r.key] = r.value;
    } });
    // emit user logged in event
    try {
        eventBus_1.default.emit({ type: 'UserLoggedIn', user_id: user.id, tenant_id: user.tenant_id || null, ip: req.ip, timestamp: new Date().toISOString() });
    }
    catch (e) { }
    if (isHx(req)) {
        res.set('HX-Redirect', '/dashboard');
        return res.status(200).send('');
    }
    res.json({ ok: true, token: access, refresh, preferences });
});
// Forgot password (example endpoint) - apply auth limiter/backoff
router.post('/forgot-password', (0, rateLimiters_1.authLimiter)(), (0, rateLimiters_1.loginBackoff)(), (0, audit_1.logAuditEvent)('user.forgot_password', (req) => ({ email: req.body.email })), async (req, res) => {
    const { email } = req.body;
    // simple stub: send reset email
    (0, mailer_1.sendMail)({ to: email, subject: 'Reset', text: 'reset link' }).catch(() => { });
    res.json({ ok: true });
});
// Refresh
router.post('/refresh', async (req, res) => {
    const { refresh } = req.body;
    const knex = (0, knex_1.knex)({ client: 'pg', connection: process.env.DATABASE_URL });
    try {
        const payload = (await Promise.resolve().then(() => __importStar(require('jsonwebtoken')))).verify(refresh, process.env.SESSION_SECRET || 'devsecret');
        const record = await knex('refresh_tokens').where({ token: refresh, user_id: payload.id }).first();
        if (!record)
            return res.status(401).json({ error: 'invalid' });
        const user = await knex('users').where({ id: payload.id }).first();
        const access = (0, auth_1.signAccessToken)({ id: user.id, tenant_id: user.tenant_id, role: user.role });
        res.json({ ok: true, token: access });
    }
    catch (err) {
        res.status(401).json({ error: 'invalid', message: err && err.message });
    }
});
// Logout
router.post('/logout', (0, audit_1.logAuditEvent)('user.logout', (req) => ({ user_id: req.user && req.user.id })), async (req, res) => {
    const { refresh } = req.body;
    const knex = (0, knex_1.knex)({ client: 'pg', connection: process.env.DATABASE_URL });
    await knex('refresh_tokens').where({ token: refresh }).del();
    res.json({ ok: true });
});
// Callback for cross-domain login — tenant subdomain should receive a token from public domain
router.get('/callback', async (req, res) => {
    const token = (req.query.token || req.query.t || '').toString();
    if (!token)
        return res.status(400).send('missing token');
    try {
        const payload = (0, auth_2.verifyToken)(token);
        // set cookie scoped to current hostname (tenant subdomain). Use httpOnly and secure when in production.
        const cookieOptions = { httpOnly: true, maxAge: 1000 * 60 * 60 * 24 * 7 };
        if (process.env.NODE_ENV === 'production')
            cookieOptions.secure = true;
        // cookie name: access_token
        res.cookie('access_token', token, cookieOptions);
        // redirect to dashboard
        return res.redirect('/dashboard');
    }
    catch (e) {
        return res.status(400).send('invalid token');
    }
});
exports.default = router;
