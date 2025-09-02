import { RequestHandler } from 'express';
import { knex } from '../db';

/**
 * resolveTenant middleware
 * - extracts subdomain from host
 * - if no subdomain or subdomain === 'www' => marks request as public (req.isPublicSite = true)
 * - if subdomain present => looks up tenant by subdomain and attaches req.tenant
 * - if tenant not found => responds 404
 */
export const resolveTenant: RequestHandler = async (req, res, next) => {
  const rawHost = (req.headers.host || req.hostname || '') as string;
  const host = rawHost.split(':')[0]; // strip port

  // prefer Express-provided subdomains when available
  let subdomain: string | undefined;
  if (Array.isArray((req as any).subdomains) && (req as any).subdomains.length) {
    // Express provides subdomains in an array (from most-specific to least-specific in some configs)
    // take the left-most label as subdomain (safer to parse host directly below)
    // fallthrough to host parsing for predictable behaviour
  }

  const parts = host.split('.');
  if (parts.length > 2) {
    subdomain = parts[0];
  }

  // treat bare domain or www as public site
  if (!subdomain || subdomain.toLowerCase() === 'www') {
    (req as any).isPublicSite = true;
    return next();
  }

  // Lookup tenant by subdomain in global tenants table
  try {
    const tenant = await (knex as any)('tenants').where({ subdomain }).first();
    if (tenant) {
      (req as any).tenant = tenant;
      return next();
    }
    // tenant not found => render a friendly landing-style error page
    try {
      return res.status(404).render('error/tenant-not-found', { title: 'Workspace non trovato' });
    } catch (e) {
      return res.status(404).send('tenant_not_found');
    }
  } catch (err) {
    console.error('resolveTenant error', err);
    return res.status(500).send('tenant_lookup_error');
  }
};
