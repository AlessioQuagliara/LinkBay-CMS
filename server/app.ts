import express from 'express';
import path from 'path';
import dotenv from 'dotenv';

import tenantResolver from './middleware/tenantResolver';
import authController from './controllers/authController';
import { initDb } from '../src/db';
import expressLayouts from 'express-ejs-layouts';
import landingRouter from './routes/landing';
import session from 'express-session';
import passport from 'passport';
import setupPassport from './middleware/passport';
import authRouter from './routes/auth';
import teamRouter from './routes/team';
import inviteRouter from './routes/invite';
import verifyMfaRouter from './routes/verifyMfa';
import tenantRouter from './routes/tenant';
import errorHandler from './middleware/errorHandler';

dotenv.config();

const app = express();
const port = process.env.PORT || 3001;

app.set('views', path.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');
app.use(expressLayouts);
// Do not set a global layout here; landing routes specify their own layout.

// Serve public assets and docs index
app.use(express.static(path.join(__dirname, '..', 'public')));
app.use('/docs', express.static(path.join(__dirname, '..', 'docs')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Attach tenant resolver early
app.use(tenantResolver);

// session + passport
app.use(
  session({
    secret: process.env.SESSION_SECRET || 'dev-secret',
    resave: false,
    saveUninitialized: false,
  })
);
setupPassport();
app.use(passport.initialize());
app.use(passport.session());

// auth
app.use('/auth', authRouter);
app.use('/team', teamRouter);
app.use('/', inviteRouter);
app.use('/', verifyMfaRouter);
app.use('/tenant', tenantRouter);

// central error handler (must be last)
app.use(errorHandler);

// Routes
// Landing pages (use per-route layout)
app.use('/', landingRouter);

// API / other controllers
app.post('/api/register', authController.register);

// Adapter endpoint: landing page can POST here with { provider, email }
// and receive a tenant-scoped redirect URL to start OAuth on the correct tenant.
app.post('/api/auth/provider-redirect', async (req, res) => {
  const { provider, email } = req.body as { provider?: string; email?: string };
  if (!provider) return res.status(400).json({ ok: false, error: 'provider required' });
  if (!email) return res.status(400).json({ ok: false, error: 'email required' });

  try {
    // Try to resolve tenant from DB if available
    let tenantSubdomain = 'default';
    try {
      const db = await initDb();
      // attempt simple matching by tenant name or by email domain
      const domain = email.split('@')[1] || '';
      const local = email.split('@')[0] || '';

      // first try by exact tenant name
      const t1 = await db('tenants').where('name', local).first();
      if (t1) tenantSubdomain = t1.name;
      else {
        const t2 = await db('tenants').where('name', domain).first();
        if (t2) tenantSubdomain = t2.name;
      }
  } catch (dbErr: any) {
      // ignore DB errors and fallback to heuristics
      // eslint-disable-next-line no-console
      console.warn('provider-redirect: DB lookup failed, falling back to heuristic', dbErr.message || dbErr);
    }

    // Build tenant URL. Support TENANT_HOST_TEMPLATE env like 'https://{subdomain}.linkbay-cms.com'
    const port = process.env.PORT || '3001';
    const hostTemplate = process.env.TENANT_HOST_TEMPLATE;
    let tenantBase = '';
    if (hostTemplate) {
      tenantBase = hostTemplate.replace('{subdomain}', tenantSubdomain).replace('{port}', String(port));
    } else {
      tenantBase = `http://${tenantSubdomain}.lvh.me:${port}`;
    }

    const redirect = `${tenantBase}/auth/${provider}`;
    return res.json({ ok: true, redirect });
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('provider-redirect error', err);
    return res.status(500).json({ ok: false, error: err.message || 'Internal error' });
  }
});

export default app;

if (require.main === module) {
  (async () => {
    try {
      await initDb();
      app.listen(port, () => {
        // eslint-disable-next-line no-console
        console.log(`Server listening on http://localhost:${port}`);
      });
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('Failed to initialize database:', err);
      process.exit(1);
    }
  })();
}
