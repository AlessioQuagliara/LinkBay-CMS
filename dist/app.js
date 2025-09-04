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
const express_1 = __importDefault(require("express"));
const path_1 = __importDefault(require("path"));
const dotenv_1 = __importDefault(require("dotenv"));
const tenantResolver_1 = require("./middleware/tenantResolver");
const resolveTenant_1 = require("./middleware/resolveTenant");
const Sentry = __importStar(require("@sentry/node"));
const compression_1 = __importDefault(require("compression"));
const express_ejs_layouts_1 = __importDefault(require("express-ejs-layouts"));
const partialCache_1 = __importDefault(require("./middleware/partialCache"));
const dynamicCors_1 = require("./middleware/dynamicCors");
const rateLimiters_1 = require("./middleware/rateLimiters");
const auth_1 = __importDefault(require("./routes/auth"));
const editor_1 = __importDefault(require("./routes/editor"));
const editorApi_1 = __importDefault(require("./routes/editorApi"));
const pages_1 = __importDefault(require("./routes/pages"));
const ssr_1 = __importDefault(require("./routes/ssr"));
const marketplace_1 = __importDefault(require("./routes/marketplace"));
const roles_1 = __importDefault(require("./routes/roles"));
const userRoles_1 = __importDefault(require("./routes/userRoles"));
const conversations_1 = __importDefault(require("./routes/conversations"));
const admin_1 = __importDefault(require("./routes/admin"));
const pluginActivity_1 = __importDefault(require("./routes/pluginActivity"));
const jwtAuth_1 = require("./middleware/jwtAuth");
const health_1 = __importDefault(require("./routes/health"));
const tenantHealth_1 = __importDefault(require("./routes/tenantHealth"));
const tenantUsage_1 = __importDefault(require("./routes/tenantUsage"));
const tenantCookieConsent_1 = __importDefault(require("./routes/tenantCookieConsent"));
const subprocessors_1 = __importDefault(require("./routes/subprocessors"));
const cookieConsent_1 = __importDefault(require("./middleware/cookieConsent"));
const tenantRateLimiter_1 = require("./middleware/tenantRateLimiter");
const tenantApiTimeout_1 = require("./middleware/tenantApiTimeout");
const status_1 = __importDefault(require("./routes/status"));
const router_1 = __importDefault(require("./plugins/router"));
const i18n_1 = require("./i18n");
const abTests_1 = require("./middleware/abTests");
const abTest_1 = require("./lib/abTest");
const swagger_ui_express_1 = __importDefault(require("swagger-ui-express"));
const swagger_jsdoc_1 = __importDefault(require("swagger-jsdoc"));
const tenantProducts_1 = __importDefault(require("./routes/api/v1/tenantProducts"));
const tenantDpia_1 = __importDefault(require("./routes/tenantDpia"));
dotenv_1.default.config();
if (process.env.SENTRY_DSN) {
    Sentry.init({ dsn: process.env.SENTRY_DSN });
}
const app = (0, express_1.default)();
app.set('views', path_1.default.join(__dirname, '..', 'views'));
app.set('view engine', 'ejs');
app.use(express_ejs_layouts_1.default);
app.use(dynamicCors_1.dynamicCors);
// Ensure JSON and urlencoded body parsing is available for early-mounted public routes
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
// public landing (marketing) should be mounted before tenant resolution
app.use('/', require('./routes/publicLanding').default);
// public auth endpoints (cross-domain login) - mounted on public site
app.use('/api/auth', require('./routes/publicAuth').default);
// resolution of tenant/public site must be early
app.use(resolveTenant_1.resolveTenant);
// compression for all responses (useful in production)
app.use((0, compression_1.default)());
// serve static assets generated into public/ with long cache headers
app.use(express_1.default.static(path_1.default.join(__dirname, '..', 'public'), { maxAge: '1y', setHeaders: (res, path) => { if (path.endsWith('.html')) {
        res.setHeader('Cache-Control', 'no-cache');
    } } }));
// global rate limiter (applies tenant/ip-based keying)
app.use((0, rateLimiters_1.globalLimiter)());
// lightweight cookie parser (only for simple cookie reads)
app.use((req, res, next) => {
    const header = req.headers && req.headers.cookie;
    req.cookies = {};
    if (header) {
        header.split(';').forEach((pair) => {
            const idx = pair.indexOf('=');
            if (idx > -1) {
                const k = pair.slice(0, idx).trim();
                const v = pair.slice(idx + 1).trim();
                try {
                    req.cookies[k] = decodeURIComponent(v);
                }
                catch (e) {
                    req.cookies[k] = v;
                }
            }
        });
    }
    next();
});
// assign AB test variants early so views can use them
app.use(abTests_1.assignAbTestVariant);
// i18n middleware
app.use(i18n_1.middleware.handle(i18n_1.i18n));
app.use('/auth', tenantResolver_1.tenantResolver, auth_1.default);
app.use('/editor', tenantResolver_1.tenantResolver, editor_1.default);
// per-tenant rate limiter and api timeout (applies after tenant resolution)
app.use(tenantResolver_1.tenantResolver);
app.use((0, tenantRateLimiter_1.tenantRateLimiter)());
app.use((0, tenantApiTimeout_1.tenantApiTimeout)());
// partial caching for rarely-changing partials (footer)
app.use(partialCache_1.default);
// OAuth SSO routes (tenant-aware config)
app.use('/auth', tenantResolver_1.tenantResolver, require('./routes/oauth').default);
// SAML endpoints
app.use('/auth/saml', tenantResolver_1.tenantResolver, require('./routes/saml').default);
// Zapier integration endpoints
app.use('/zapier', tenantResolver_1.tenantResolver, require('./routes/zapier').default);
// Integration builders (HubSpot, Salesforce, etc.)
app.use('/integrations', tenantResolver_1.tenantResolver, require('./routes/integrations').default);
// Public integration marketplace
app.use('/api/integrations', require('./routes/publicIntegrations').default);
app.use('/api/tenant/integrations', tenantResolver_1.tenantResolver, require('./routes/publicIntegrations').default);
// preview endpoint (transient) - no tenant persistence
app.use('/api/editor', editorApi_1.default);
app.use('/api/pages', tenantResolver_1.tenantResolver, pages_1.default);
app.use('/api/products', tenantResolver_1.tenantResolver, require('./routes/products').default);
app.use('/api/cart', tenantResolver_1.tenantResolver, require('./routes/cart').default);
app.use('/api/marketplace', tenantResolver_1.tenantResolver, marketplace_1.default);
// block templates (tenant-aware)
app.use('/api/block-templates', tenantResolver_1.tenantResolver, require('./routes/blockTemplates').default);
// tenant settings
app.use('/api/tenant/settings', tenantResolver_1.tenantResolver, require('./routes/tenantSettings').default);
// menus
app.use('/api/menus', tenantResolver_1.tenantResolver, require('./routes/menus').default);
// analytics API (tenant scoped)
app.use('/api/analytics', tenantResolver_1.tenantResolver, require('./routes/analytics').default);
// scheduled reports
app.use('/api/reports', tenantResolver_1.tenantResolver, require('./routes/scheduledReports').default);
// tenant dashboard pages (require tenant resolution)
app.use('/dashboard', tenantResolver_1.tenantResolver, require('./routes/dashboard').default);
// tenant settings API
app.use('/api/settings', tenantResolver_1.tenantResolver, require('./routes/settings').default);
// Public Tenant API (API-Key authenticated)
app.use('/api/v1/tenant', tenantProducts_1.default);
// Tenant DPIA / Data Processing Activities (tenant-aware)
app.use('/api/tenant/data-processing-activities', tenantResolver_1.tenantResolver, tenantDpia_1.default);
// Swagger/OpenAPI
const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: { title: 'LinkBay CMS Tenant API', version: '1.0.0' }
    },
    apis: [path_1.default.join(__dirname, '/routes/api/**/*.ts')]
};
const swaggerSpec = (0, swagger_jsdoc_1.default)(swaggerOptions);
app.use('/api-docs', swagger_ui_express_1.default.serve, swagger_ui_express_1.default.setup(swaggerSpec));
// admin RBAC management (requires appropriate permissions enforced in routes)
app.use('/api/admin/roles', tenantResolver_1.tenantResolver, roles_1.default);
app.use('/api/admin/users', tenantResolver_1.tenantResolver, userRoles_1.default);
app.use('/api/admin', require('./routes/adminAnonymize').default);
app.use('/api/conversations', tenantResolver_1.tenantResolver, conversations_1.default);
// user onboarding status
app.use('/api/user', require('./routes/onboarding').default);
// user preferences
app.use('/api/user/preferences', require('./routes/userPreferences').default);
// admin UI and APIs (super_admin/permission protected)
// Admin interface requires authentication + permission (no tenant resolution)
app.use('/admin', jwtAuth_1.jwtAuth, admin_1.default);
// plugin activity dashboard (admin only)
app.use('/admin/plugin-activity', jwtAuth_1.jwtAuth, pluginActivity_1.default);
// content audit routes (admin)
app.use('/api/admin/content-audit', jwtAuth_1.jwtAuth, require('./routes/contentAudit').default);
// health endpoints (no auth)
app.use('/health', health_1.default);
app.use('/api/tenant/health', tenantHealth_1.default);
app.use('/api/tenant/usage', tenantUsage_1.default);
// tenant cookie consent API
app.use('/api/tenant/cookie-consent', tenantCookieConsent_1.default);
// inject cookie consent helper for templates
app.use(cookieConsent_1.default);
// public status page and JSON
app.use('/', status_1.default);
// public subprocessors API and public legal page
app.use('/api/subprocessors', subprocessors_1.default);
app.get('/legal/subprocessors', async (req, res) => {
    // server-side render page; page will fetch the API itself for fresh data (client-side)
    res.render('legal/subprocessors', { subprocessors: null });
});
// plugin routes namespace
app.use('/api/plugin', router_1.default);
// Sentry error handler (capture exceptions)
// Capture errors to Sentry (if configured) using a custom error handler
if (process.env.SENTRY_DSN) {
    app.use((err, req, res, next) => {
        try {
            Sentry.captureException(err);
        }
        catch (e) { /* ignore */ }
        next(err);
    });
}
app.get('/', (req, res) => res.render('index', { title: 'LinkBayCMS' }));
// expose t to EJS templates
app.use((req, res, next) => {
    res.locals.t = (key, opts) => req.t ? req.t(key, opts) : i18n_1.i18n.t(key, opts);
    // expose abTest helper to templates
    res.locals.abTest = (testName, variantMap) => (0, abTest_1.abTestHelper)(req, testName, variantMap);
    next();
});
// server-side rendered pages (marketing + tenant pages)
app.use('/', ssr_1.default);
exports.default = app;
