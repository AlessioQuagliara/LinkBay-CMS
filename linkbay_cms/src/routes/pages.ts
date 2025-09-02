import { Router } from 'express';
import { knex } from '../db';

const router = Router();

// Create or update page (supports language field)
router.post('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { id, name, slug, content_json, content_html, language } = req.body;
  const lang = language || 'en';
  if (id) {
    await knex('pages').where({ id, tenant_id: tenant.id }).update({ name, slug, content_json, content_html, language: lang, updated_at: knex.fn.now() });
    return res.json({ ok: true, id });
  }
  const [newId] = await knex('pages').insert({ tenant_id: tenant.id, name, slug, content_json, content_html, language: lang }).returning('id');
  res.json({ ok: true, id: newId });
});

// List pages for tenant (optionally filter by language)
router.get('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const lang = (req.query.lang as string) || undefined;
  const q = knex('pages').where({ tenant_id: tenant.id });
  if (lang) q.andWhere('language', lang);
  const rows = await q.select('id', 'name', 'slug', 'language', 'created_at', 'updated_at');
  res.json(rows);
});

// Internal: Get page by id
router.get('/:id', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const row = await knex('pages').where({ id: req.params.id, tenant_id: tenant.id }).first();
  if (!row) return res.status(404).json({ error: 'not_found' });
  res.json(row);
});

// Public route should be served by SSR router; however expose helper to get by slug+language
router.get('/by-slug/:lang/:slug', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { lang, slug } = req.params;
  const row = await knex('pages').where({ tenant_id: tenant.id, slug, language: lang }).first();
  if (!row) return res.status(404).json({ error: 'not_found' });
  res.json(row);
});

export default router;
