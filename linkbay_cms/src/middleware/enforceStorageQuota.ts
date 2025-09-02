import { RequestHandler } from 'express';
import { knex } from '../db';

export const enforceStorageQuota: RequestHandler = async (req:any, res, next) => {
  try {
    const tenantId = req.tenant && req.tenant.id ? req.tenant.id : req.headers['x-tenant-id'];
    if (!tenantId) return res.status(400).json({ error: 'no_tenant' });
    const row:any = await knex('tenants').where({ id: tenantId }).first();
    if (!row) return res.status(404).json({ error: 'tenant_not_found' });
    if (!row.storage_quota_bytes) return next();
    // sum sizes of existing tenant media
    const [{ total }]: any = await knex('media').where({ tenant_id: tenantId }).sum('size_bytes as total');
    const used = Number(total || 0);
    // get incoming file size from header or body (middleware should be used before file is written)
    const incoming = Number(req.headers['x-upload-bytes'] || req.body && req.body.size || 0);
    if (used + incoming > Number(row.storage_quota_bytes)) return res.status(413).json({ error: 'storage_quota_exceeded' });
    next();
  } catch (e) {
    next(e);
  }
};
