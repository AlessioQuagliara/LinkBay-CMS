import express from 'express';
import path from 'path';
import dotenv from 'dotenv';
import { tenantResolver } from './middleware/tenantResolver';
import { resolveTenant } from './middleware/resolveTenant';
import * as Sentry from '@sentry/node';
import compression from 'compression';
import expressLayouts from 'express-ejs-layouts';
import partialCacheMiddleware from './middleware/partialCache';
import { dynamicCors } from './middleware/dynamicCors';
import { globalLimiter } from './middleware/rateLimiters';
import authRouter from './routes/auth';
import editorRouter from './routes/editor';
import editorApiRouter from './routes/editorApi';
import pagesRouter from './routes/pages';
import ssrRouter from './routes/ssr';
import marketplaceRouter from './routes/marketplace';
import rolesRouter from './routes/roles';
import userRolesRouter from './routes/userRoles';
import conversationsRouter from './routes/conversations';
import adminRouter from './routes/admin';
import pluginActivityRouter from './routes/pluginActivity';
import { jwtAuth } from './middleware/jwtAuth';
import healthRouter from './routes/health';
import tenantHealthRoutes from './routes/tenantHealth';
import tenantUsageRoutes from './routes/tenantUsage';
import tenantCookieConsent from './routes/tenantCookieConsent';
import subprocessorsRouter from './routes/subprocessors';
import cookieConsentMiddleware from './middleware/cookieConsent';
import { tenantRateLimiter } from './middleware/tenantRateLimiter';
import { tenantApiTimeout } from './middleware/tenantApiTimeout';
import statusRouter from './routes/status';
import pluginRouter from './plugins/router';
import { i18n, middleware as i18nMiddleware } from './i18n';
import { assignAbTestVariant } from './middleware/abTests';
import { abTestHelper } from './lib/abTest';
import swaggerUi from 'swagger-ui-express';
import swaggerJSDoc from 'swagger-jsdoc';
import tenantApiRouter from './routes/api/v1/tenantProducts';
import tenantDpiaRouter from './routes/tenantDpia';
dotenv.config();

if (process.env.SENTRY_DSN) {
	Sentry.init({ dsn: process.env.SENTRY_DSN });
}

const app = express();
app.set('views', path.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');
app.use(expressLayouts);
app.use(dynamicCors);
// public landing (marketing) should be mounted before tenant resolution
app.use('/', require('./routes/publicLanding').default);
// public auth endpoints (cross-domain login) - mounted on public site
app.use('/api/auth', require('./routes/publicAuth').default);
// resolution of tenant/public site must be early
app.use(resolveTenant);

// compression for all responses (useful in production)
app.use(compression());

// serve static assets generated into public/ with long cache headers
app.use(express.static(path.join(__dirname, '..', 'public'), { maxAge: '1y', setHeaders: (res, path) => { if (path.endsWith('.html')) { res.setHeader('Cache-Control', 'no-cache'); } } }));
// global rate limiter (applies tenant/ip-based keying)
app.use(globalLimiter());
// lightweight cookie parser (only for simple cookie reads)
app.use((req: any, res, next) => {
	const header = req.headers && req.headers.cookie;
	req.cookies = {};
	if (header) {
		header.split(';').forEach((pair:string) => {
			const idx = pair.indexOf('=');
			if (idx > -1) {
				const k = pair.slice(0, idx).trim();
				const v = pair.slice(idx+1).trim();
				try { req.cookies[k] = decodeURIComponent(v); } catch(e) { req.cookies[k] = v; }
			}
		});
	}
	next();
});
// assign AB test variants early so views can use them
app.use(assignAbTestVariant);
// i18n middleware
app.use(i18nMiddleware.handle(i18n));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use('/auth', tenantResolver, authRouter);
app.use('/editor', tenantResolver, editorRouter);
// per-tenant rate limiter and api timeout (applies after tenant resolution)
app.use(tenantResolver);
app.use(tenantRateLimiter());
app.use(tenantApiTimeout());
// partial caching for rarely-changing partials (footer)
app.use(partialCacheMiddleware);
// OAuth SSO routes (tenant-aware config)
app.use('/auth', tenantResolver, require('./routes/oauth').default);
// SAML endpoints
app.use('/auth/saml', tenantResolver, require('./routes/saml').default);
// Zapier integration endpoints
app.use('/zapier', tenantResolver, require('./routes/zapier').default);

// Integration builders (HubSpot, Salesforce, etc.)
app.use('/integrations', tenantResolver, require('./routes/integrations').default);

// Public integration marketplace
app.use('/api/integrations', require('./routes/publicIntegrations').default);
app.use('/api/tenant/integrations', tenantResolver, require('./routes/publicIntegrations').default);
// preview endpoint (transient) - no tenant persistence
app.use('/api/editor', editorApiRouter);
app.use('/api/pages', tenantResolver, pagesRouter);
app.use('/api/products', tenantResolver, require('./routes/products').default);
app.use('/api/cart', tenantResolver, require('./routes/cart').default);
app.use('/api/marketplace', tenantResolver, marketplaceRouter);
// block templates (tenant-aware)
app.use('/api/block-templates', tenantResolver, require('./routes/blockTemplates').default);
// tenant settings
app.use('/api/tenant/settings', tenantResolver, require('./routes/tenantSettings').default);
// menus
app.use('/api/menus', tenantResolver, require('./routes/menus').default);
// analytics API (tenant scoped)
app.use('/api/analytics', tenantResolver, require('./routes/analytics').default);
// scheduled reports
app.use('/api/reports', tenantResolver, require('./routes/scheduledReports').default);
// tenant dashboard pages (require tenant resolution)
app.use('/dashboard', tenantResolver, require('./routes/dashboard').default);

// tenant settings API
app.use('/api/settings', tenantResolver, require('./routes/settings').default);

// Public Tenant API (API-Key authenticated)
app.use('/api/v1/tenant', tenantApiRouter);

// Tenant DPIA / Data Processing Activities (tenant-aware)
app.use('/api/tenant/data-processing-activities', tenantResolver, tenantDpiaRouter);

// Swagger/OpenAPI
const swaggerOptions = {
	definition: {
		openapi: '3.0.0',
		info: { title: 'LinkBay CMS Tenant API', version: '1.0.0' }
	},
	apis: [path.join(__dirname, '/routes/api/**/*.ts')]
};
const swaggerSpec = swaggerJSDoc(swaggerOptions as any);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
// admin RBAC management (requires appropriate permissions enforced in routes)
app.use('/api/admin/roles', tenantResolver, rolesRouter);
app.use('/api/admin/users', tenantResolver, userRolesRouter);
app.use('/api/admin', require('./routes/adminAnonymize').default);
app.use('/api/conversations', tenantResolver, conversationsRouter);
// user onboarding status
app.use('/api/user', require('./routes/onboarding').default);

// user preferences
app.use('/api/user/preferences', require('./routes/userPreferences').default);

// admin UI and APIs (super_admin/permission protected)
// Admin interface requires authentication + permission (no tenant resolution)
app.use('/admin', jwtAuth, adminRouter);
// plugin activity dashboard (admin only)
app.use('/admin/plugin-activity', jwtAuth, pluginActivityRouter);
// content audit routes (admin)
app.use('/api/admin/content-audit', jwtAuth, require('./routes/contentAudit').default);

// health endpoints (no auth)
app.use('/health', healthRouter);
app.use('/api/tenant/health', tenantHealthRoutes);
app.use('/api/tenant/usage', tenantUsageRoutes);
// tenant cookie consent API
app.use('/api/tenant/cookie-consent', tenantCookieConsent);
// inject cookie consent helper for templates
app.use(cookieConsentMiddleware);
// public status page and JSON
app.use('/', statusRouter);
// public subprocessors API and public legal page
app.use('/api/subprocessors', subprocessorsRouter);
app.get('/legal/subprocessors', async (req, res) => {
	// server-side render page; page will fetch the API itself for fresh data (client-side)
	res.render('legal/subprocessors', { subprocessors: null });
});
// plugin routes namespace
app.use('/api/plugin', pluginRouter);

// Sentry error handler (capture exceptions)
// Capture errors to Sentry (if configured) using a custom error handler
if (process.env.SENTRY_DSN) {
	app.use((err: any, req: any, res: any, next: any) => {
		try { Sentry.captureException(err); } catch (e) { /* ignore */ }
		next(err);
	});
}

app.get('/', (req, res) => res.render('index', { title: 'LinkBayCMS' }));

// expose t to EJS templates
app.use((req, res, next) => {
	res.locals.t = (key: string, opts?: any) => (req as any).t ? (req as any).t(key, opts) : i18n.t(key, opts);
	// expose abTest helper to templates
	(res as any).locals.abTest = (testName: string, variantMap: Record<string,string>) => abTestHelper(req, testName, variantMap);
	next();
});

// server-side rendered pages (marketing + tenant pages)
app.use('/', ssrRouter);

export default app;
