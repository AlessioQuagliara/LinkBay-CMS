"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.renderPage = renderPage;
const db_1 = require("../db");
const dbMultiTenant_1 = require("../dbMultiTenant");
const eventBus_1 = __importDefault(require("../lib/eventBus"));
const MAIN_DOMAIN = process.env.MAIN_DOMAIN || 'yourplatform.com';
async function renderPage(req, res) {
    const hostRaw = req.hostname || req.headers.host || '';
    const host = hostRaw.split(':')[0];
    const parts = host.split('.');
    let subdomain;
    if (parts.length > 2)
        subdomain = parts[0];
    // If the path looks like a static asset (contains an extension) skip SSR rendering
    if (req.path && req.path.includes('.')) {
        return res.status(404).send();
    }
    const isMainDomain = host === MAIN_DOMAIN || host === `www.${MAIN_DOMAIN}`;
    // marketing site when targeting main domain or no subdomain
    if (!subdomain || isMainDomain) {
        const slug = req.path === '/' ? 'home' : req.path.replace(/^\/+/, '');
        const view = slug === '' || slug === 'home' ? 'marketing/home' : `marketing/${slug}`;
        // render marketing view if exists; set short client/CDN cache
        res.setHeader('Cache-Control', 'public, max-age=60, s-maxage=60');
        return res.render(view, { title: slug || 'Home' });
    }
    // tenant site: resolve tenant by subdomain
    const tenant = await db_1.knex('tenants').where({ subdomain }).first();
    if (!tenant)
        return res.status(404).render('marketing/404', { title: 'Tenant not found' });
    const slug = req.path === '/' ? 'home' : req.path.replace(/^\/+/, '');
    // Try to load page from tenant schema first
    try {
        const tenantDb = (0, dbMultiTenant_1.getTenantDB)(tenant.id);
        let page = await tenantDb('pages').where({ slug }).first();
        if (!page) {
            // fallback to public pages table (tenant-scoped)
            page = await db_1.knex('pages').where({ tenant_id: tenant.id, slug }).first();
        }
        if (!page)
            return res.status(404).render('marketing/404', { title: 'Page not found' });
        // emit page view event
        try {
            eventBus_1.default.emit({ type: 'PageView', tenant_id: tenant.id, path: req.path, hostname: req.hostname, user_id: req.user ? req.user.id : null, timestamp: new Date().toISOString() });
        }
        catch (e) { }
        // tenant public pages: short cache
        res.setHeader('Cache-Control', 'public, max-age=120, s-maxage=120');
        return res.render('layouts/boilerplate', {
            title: page.name || slug,
            tenant,
            content_html: page.content_html || ''
        });
    }
    catch (err) {
        console.error('renderPage error', err && err.message);
        return res.status(500).render('marketing/500', { title: 'Server error' });
    }
}
exports.default = { renderPage };
