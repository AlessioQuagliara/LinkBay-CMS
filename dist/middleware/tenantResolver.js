"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tenantResolver = void 0;
const db_1 = require("../db");
const dbMultiTenant_1 = require("../dbMultiTenant");
const tenantResolver = async (req, res, next) => {
    const rawHost = (req.headers.host || req.hostname || '');
    const host = rawHost.split(':')[0]; // strip port
    const xTenantHeader = req.headers['x-tenant-id'];
    let subdomain;
    let tenant = null;
    if (xTenantHeader) {
        const asNum = Number(xTenantHeader);
        if (!Number.isNaN(asNum) && String(asNum) === String(xTenantHeader)) {
            // X-Tenant-Id provided as numeric tenant id
            tenant = await db_1.knex('tenants').where({ id: asNum }).first();
        }
        else {
            // X-Tenant-Id provided as subdomain string
            subdomain = xTenantHeader;
        }
    }
    if (!tenant && host) {
        const parts = host.split('.');
        if (parts.length > 2)
            subdomain = parts[0];
        else if (parts.length === 2) {
            // Accept dev host patterns like test-tenant.localhost or test-tenant.lvh.me
            const second = parts[1].toLowerCase();
            if (second === 'localhost' || second === 'lvh' || second === 'lvh.me' || second === 'local')
                subdomain = parts[0];
        }
        if (subdomain)
            tenant = await db_1.knex('tenants').where({ subdomain }).first();
    }
    if (!tenant)
        return res.status(404).json({ error: 'tenant_not_found' });
    req.tenant = tenant;
    // attach helper to get a region-aware tenant DB connection
    req.getTenantDB = async () => {
        return await (0, dbMultiTenant_1.getTenantDBAsync)(tenant.id);
    };
    try {
        const settings = await db_1.knex('tenant_settings').where({ tenant_id: tenant.id }).first();
        req.tenantSettings = settings || null;
        res.locals.tenantSettings = settings || null;
    }
    catch (e) {
        req.tenantSettings = null;
        res.locals.tenantSettings = null;
    }
    next();
};
exports.tenantResolver = tenantResolver;
