import { Router } from 'express';
import { getTenantDB } from '../dbMultiTenant';
import crypto from 'crypto';
import { hashPassword } from '../services/auth';

const router = Router();

// List API keys (for page rendering)
router.get('/api-keys', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const k = req.getTenantDB ? await req.getTenantDB() : getTenantDB(tenant.id);
  const rows = await k('api_keys').where({ tenant_id: tenant.id }).orderBy('created_at', 'desc').select('id','name','key_masked','created_at');
  res.json(rows);
});

// Create API key: returns partial with full key visible only on creation
router.post('/api-keys', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { name } = req.body;
  const k = req.getTenantDB ? await req.getTenantDB() : getTenantDB(tenant.id);
  const raw = crypto.randomBytes(32).toString('hex');
  const keyHash = await hashPassword(raw);
  const masked = raw.slice(0,6) + '...' + raw.slice(-6);
  const [id] = await k('api_keys').insert({ tenant_id: tenant.id, name, key_hash: keyHash, key_masked: masked }).returning('id');
  // return an HTML snippet that includes the full key (only now)
  return res.send(`<div class="p-3 bg-green-50 text-green-800 rounded">Chiave creata: <code class=\"font-mono\">${raw}</code></div><script>htmx.trigger(document.querySelector('#api-keys-list'), 'refresh')</script>`);
});

// Delete API key
router.delete('/api-keys/:id', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const id = Number(req.params.id);
  const k = req.getTenantDB ? await req.getTenantDB() : getTenantDB(tenant.id);
  await k('api_keys').where({ id, tenant_id: tenant.id }).del();
  // return updated list partial (simpler: return a small message)
  return res.send('<div class="p-2 text-sm text-green-800 bg-green-50 rounded">Chiave eliminata</div><script>htmx.ajax("GET","/api/settings/api-keys?partial=list",{target:document.querySelector("#api-keys-list"),swap:"outerHTML"})</script>');
});

// Webhooks
router.post('/webhooks', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { url, events } = req.body;
  const k = req.getTenantDB ? await req.getTenantDB() : getTenantDB(tenant.id);
  const [id] = await k('webhooks').insert({ tenant_id: tenant.id, url, events }).returning('id');
  // return a new row partial to append
  return res.render('settings/partials/webhook-row', { w: { id, url, events } });
});

router.delete('/webhooks/:id', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const id = Number(req.params.id);
  const k = req.getTenantDB ? await req.getTenantDB() : getTenantDB(tenant.id);
  await k('webhooks').where({ id, tenant_id: tenant.id }).del();
  return res.send('<div class="p-2 text-sm text-green-800 bg-green-50 rounded">Webhook eliminato</div>');
});

export default router;
