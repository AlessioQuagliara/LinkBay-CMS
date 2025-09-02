import { Router } from 'express';
import { knex } from '../db';
import { tenantResolver } from '../middleware/tenantResolver';

const router = Router();
router.use(tenantResolver);

// GET current config for tenant
router.get('/', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(400).json({ error: 'tenant_required' });
  try {
    const row = await knex('tenant_cookie_consent').where({ tenant_id: tenant.id }).first();
    res.json({ success: true, config: row || null });
  } catch (e:any) { res.status(500).json({ error: 'server_error' }); }
});

// POST update config for tenant
router.post('/', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(400).json({ error: 'tenant_required' });
  const { banner_text, necessary_cookies, analytics_cookies, marketing_cookies, enabled } = req.body;
  try {
    const existing = await knex('tenant_cookie_consent').where({ tenant_id: tenant.id }).first();
    if (existing) {
      await knex('tenant_cookie_consent').where({ tenant_id: tenant.id }).update({ banner_text, necessary_cookies, analytics_cookies, marketing_cookies, enabled, updated_at: new Date() });
    } else {
      await knex('tenant_cookie_consent').insert({ tenant_id: tenant.id, banner_text, necessary_cookies, analytics_cookies, marketing_cookies, enabled });
    }
    res.json({ success: true });
  } catch (e:any) { console.error('save cookie config failed', e); res.status(500).json({ error: 'server_error' }); }
});

export default router;
