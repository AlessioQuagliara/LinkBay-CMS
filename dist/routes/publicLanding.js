"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const router = (0, express_1.Router)();
// ensure form bodies are parsed for this router (mounted early in app.ts)
router.use((0, express_1.urlencoded)({ extended: true }));
router.get('/', (req, res) => {
    res.render('landing/home', { layout: 'landing/_layout', title: 'LinkBay CMS — Welcome' });
});
router.get('/features', (req, res) => {
    res.render('landing/features', { layout: 'landing/_layout', title: 'Features — LinkBay CMS' });
});
router.get('/pricing', (req, res) => {
    res.render('landing/pricing', { layout: 'landing/_layout', title: 'Pricing — LinkBay CMS' });
});
router.get('/login', (req, res) => {
    res.render('landing/login', { layout: 'landing/_layout', title: 'Login — LinkBay CMS' });
});
router.get('/signup', (req, res) => {
    res.render('landing/signup', { layout: 'landing/_layout', title: 'Sign up — LinkBay CMS' });
});
// simple redirector to tenant subdomain for login (now accepts POST from the public form)
router.post('/login-redirect', async (req, res) => {
    // Prefer body (form POST) but accept query for backward compatibility
    const tenantParam = ((req.body && req.body.tenant) || req.query.tenant || '').toString().trim();
    const emailParam = (((req.body && req.body.email) || req.query.email) || '').toString().trim().toLowerCase();
    if (!tenantParam && !emailParam)
        return res.redirect('/login');
    let tenantSubdomain = tenantParam || '';
    try {
        if (!tenantSubdomain && emailParam) {
            // find user across tenants by email and prefer tenant_admin/agency roles
            const user = await (require('../db').knex)('users')
                .whereRaw('lower(email) = ?', [emailParam])
                .orderByRaw("case when role = 'tenant_admin' then 1 when role = 'agency' then 2 else 3 end")
                .first();
            if (user) {
                const t = await (require('../db').knex)('tenants').where({ id: user.tenant_id }).first();
                if (t)
                    tenantSubdomain = t.subdomain;
            }
        }
    }
    catch (e) {
        // ignore DB errors and fall back to tenantParam if provided
    }
    // Development fallback: if DB not reachable or tenant not found, allow demo emails to resolve to demo tenant
    try {
        if (!tenantSubdomain && process.env.NODE_ENV !== 'production') {
            if ((emailParam && emailParam.endsWith('@demo.com')) || tenantParam === 'demo') {
                tenantSubdomain = 'demo';
            }
        }
    }
    catch (e) {
        // ignore
    }
    if (!tenantSubdomain)
        return res.status(404).json({ error: 'tenant_not_found' });
    // Build redirect target (local dev vs production), preserve previous behavior
    const rawHost = (req.headers.host || '').toString();
    const hostNoPort = rawHost.split(':')[0];
    const port = process.env.PORT || '3001';
    let target = '';
    try {
        const isLocal = hostNoPort === 'localhost' || hostNoPort.endsWith('.localhost') || hostNoPort === 'lvh.me' || hostNoPort.endsWith('.lvh.me');
        if (isLocal) {
            const base = hostNoPort === 'localhost' ? 'localhost' : hostNoPort;
            target = `http://${tenantSubdomain}.${base}:${port}`;
        }
        else if (process.env.APP_URL) {
            const u = new URL(process.env.APP_URL);
            const base = u.hostname;
            const scheme = u.protocol.replace(':', '') || 'http';
            const uPort = u.port ? `:${u.port}` : '';
            target = `${scheme}://${tenantSubdomain}.${base}${uPort}`;
        }
        else {
            target = `http://${tenantSubdomain}.yoursite-linkbay-cms.com`;
        }
    }
    catch (err) {
        target = `http://${tenantSubdomain}.yoursite-linkbay-cms.com`;
    }
    res.redirect(target);
});
// simple signup handler (creates tenant) - lightweight placeholder
router.post('/signup', async (req, res) => {
    const { subdomain, email, password } = req.body;
    if (!subdomain || !email || !password)
        return res.status(400).send('missing');
    // NOTE: real implementation should validate, create tenant record, hashed password, send confirmation, etc.
    // For now redirect to a success page or to the tenant subdomain
    return res.redirect(`http://${subdomain}.yoursite-linkbay-cms.com`);
});
exports.default = router;
