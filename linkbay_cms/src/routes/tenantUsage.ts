import express from 'express';
import { knex } from '../db';
const router = express.Router();

// admin-only: show tenant usage
router.get('/', async (req:any, res) => {
  const tenantId = req.tenant && req.tenant.id ? req.tenant.id : req.headers['x-tenant-id'];
  if (!tenantId) return res.status(400).json({ error: 'no_tenant' });
  const tenant:any = await knex('tenants').where({ id: tenantId }).first();
  if (!tenant) return res.status(404).json({ error: 'tenant_not_found' });
  const [{ total }]: any = await knex('media').where({ tenant_id: tenantId }).sum('size_bytes as total');
  const storageUsed = Number(total || 0);
  const bandwidth = Number(tenant.monthly_bandwidth_bytes || 0);
  res.json({ tenant: tenantId, storageQuota: tenant.storage_quota_bytes || null, storageUsed, monthlyBandwidthUsed: bandwidth });
});

export default router;
