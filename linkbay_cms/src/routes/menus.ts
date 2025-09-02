import { Router } from 'express';
import { knex } from '../db';

const router = Router();

// List menus for tenant
router.get('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if(!tenant) return res.status(404).json({ error: 'tenant_required' });
  const rows = await knex('menus').where({ tenant_id: tenant.id }).orderBy('created_at','desc');
  res.json(rows);
});

// Create or update menu
router.post('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if(!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { id, name, location, items } = req.body;
  const payload = { tenant_id: tenant.id, name, location, items: JSON.stringify(items || []) };
  if(id) {
    await knex('menus').where({ id, tenant_id: tenant.id }).update({ ...payload, updated_at: knex.fn.now() });
    return res.json({ ok: true });
  }
  const [newId] = await knex('menus').insert(payload).returning('id');
  res.json({ ok: true, id: newId });
});

// Delete menu
router.delete('/:id', async (req, res) => {
  const tenant = (req as any).tenant;
  if(!tenant) return res.status(404).json({ error: 'tenant_required' });
  const id = Number(req.params.id);
  await knex('menus').where({ id, tenant_id: tenant.id }).del();
  res.json({ ok: true });
});

// Public: get menu for tenant by location (no auth, tenantResolver must set tenant)
router.get('/public/:location', async (req, res) => {
  const tenant = (req as any).tenant;
  if(!tenant) return res.status(404).json({ error: 'tenant_required' });
  const loc = req.params.location;
  const row = await knex('menus').where({ tenant_id: tenant.id, location: loc }).first();
  res.json(row || { items: [] });
});

export default router;
