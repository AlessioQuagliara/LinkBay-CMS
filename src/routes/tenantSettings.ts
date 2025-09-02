import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';
import { auditChange } from '../middleware/audit';

function sanitizeTrackingScript(input: string): string | null {
  if (!input || typeof input !== 'string') return null;
  const lowered = input.toLowerCase();
  // allowlist simple checks for common providers
  const allowPatterns = ['googletagmanager.com', 'gtag(', 'google-analytics.com', 'connect.facebook.net', 'fbq(', 'facebook.com/tr', 'adsbygoogle', 'googlesyndication'];
  const ok = allowPatterns.some(p => lowered.includes(p));
  if (!ok) return null;
  // minimal sanitize: strip out <script> tags with inline event handlers by removing 'onerror=' etc
  // Note: this is a basic heuristic; for production use a robust sanitizer like DOMPurify on the server or store scripts as-is but restrict access.
  return input.replace(/on\w+\s*=\s*\"[^\"]*\"/gi, '').replace(/on\w+\s*=\s*\'[^\']*\'/gi, '');
}

const router = Router();

// GET /api/tenant/settings
router.get('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const row = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  res.json(row || {});
});

// PUT /api/tenant/settings
router.put('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { primary_color, secondary_color, logo_url, favicon_url, css_overrides, default_theme } = req.body;
  const exists = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  const payload = { primary_color, secondary_color, logo_url, favicon_url, css_overrides, default_theme };
  if (exists) {
  const before = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  await knex('tenant_settings').where({ tenant_id: tenant.id }).update({ ...payload, updated_at: knex.fn.now() });
  try { await auditChange('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: before, newValue: { ...before, ...payload } }); } catch(e){}
  } else {
  await knex('tenant_settings').insert({ tenant_id: tenant.id, ...payload });
  try { await auditChange('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: null, newValue: payload }); } catch(e){}
  }
  const row = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  res.json(row);
});

// PUT /api/tenant/tracking-scripts
router.put('/tracking-scripts', requirePermission('settings.manage'), async (req:any, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { tracking_scripts } = req.body;
  const sanitized = sanitizeTrackingScript(tracking_scripts);
  if (tracking_scripts && !sanitized) return res.status(400).json({ error: 'invalid_tracking_scripts' });
  const exists = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  if (exists) {
  const before = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  await knex('tenant_settings').where({ tenant_id: tenant.id }).update({ tracking_scripts: sanitized, updated_at: knex.fn.now() });
  try { await auditChange('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: before, newValue: { ...before, tracking_scripts: sanitized } }); } catch(e){}
  } else {
  await knex('tenant_settings').insert({ tenant_id: tenant.id, tracking_scripts: sanitized });
  try { await auditChange('TENANT_SETTINGS_UPDATED', { tenantId: tenant.id, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: null, newValue: { tracking_scripts: sanitized } }); } catch(e){}
  }
  const row = await knex('tenant_settings').where({ tenant_id: tenant.id }).first();
  res.json(row);
});

export default router;
