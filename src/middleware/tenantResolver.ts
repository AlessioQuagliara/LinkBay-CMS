import { RequestHandler } from 'express';
import { knex } from '../db';
import { getTenantDBAsync } from '../dbMultiTenant';

export const tenantResolver: RequestHandler = async (req, res, next) => {
  const rawHost = (req.headers.host || req.hostname || '') as string;
  const host = rawHost.split(':')[0]; // strip port
  const xTenantHeader = req.headers['x-tenant-id'] as string | undefined;

  let subdomain: string | undefined;
  let tenant: any | null = null;

  if (xTenantHeader) {
    const asNum = Number(xTenantHeader);
    if (!Number.isNaN(asNum) && String(asNum) === String(xTenantHeader)) {
      // X-Tenant-Id provided as numeric tenant id
      tenant = await (knex as any)('tenants').where({ id: asNum }).first();
    } else {
      // X-Tenant-Id provided as subdomain string
      subdomain = xTenantHeader;
    }
  }

  if (!tenant && host) {
    const parts = host.split('.');
    if (parts.length > 2) subdomain = parts[0];
    else if (parts.length === 2) {
      // Accept dev host patterns like test-tenant.localhost or test-tenant.lvh.me
      const second = parts[1].toLowerCase();
      if (second === 'localhost' || second === 'lvh' || second === 'lvh.me' || second === 'local') subdomain = parts[0];
    }
    if (subdomain) tenant = await (knex as any)('tenants').where({ subdomain }).first();
  }

  if (!tenant) return res.status(404).json({ error: 'tenant_not_found' });
  (req as any).tenant = tenant;
  // attach helper to get a region-aware tenant DB connection
  (req as any).getTenantDB = async () => {
    return await getTenantDBAsync(tenant.id);
  };
  try {
    const settings = await (knex as any)('tenant_settings').where({ tenant_id: tenant.id }).first();
    (req as any).tenantSettings = settings || null;
    (res as any).locals.tenantSettings = settings || null;
  } catch (e) {
    (req as any).tenantSettings = null;
    (res as any).locals.tenantSettings = null;
  }
  next();
};
