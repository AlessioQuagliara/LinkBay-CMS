import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';

const router = Router();
router.use(requirePermission('admin.view'));

// list page versions
router.get('/pages/:id/versions', async (req, res) => {
  const id = Number(req.params.id);
  try {
    const rows = await knex('pages_audit').where({ page_id: id }).orderBy('version', 'desc').select('*');
    res.json({ success: true, versions: rows });
  } catch (e:any) { res.status(500).json({ error: 'server_error' }); }
});

// rollback page to a specific version
router.post('/pages/:id/rollback/:version', async (req, res) => {
  const id = Number(req.params.id);
  const version = Number(req.params.version);
  try {
    const snap = await knex('pages_audit').where({ page_id: id, version }).first();
    if (!snap) return res.status(404).json({ error: 'not_found' });
    await knex('pages').where({ id }).update({ name: snap.name, content_json: snap.content_json, content_html: snap.content_html, slug: snap.slug, updated_at: new Date() });
    res.json({ success: true });
  } catch (e:any) { res.status(500).json({ error: 'server_error' }); }
});

// list product versions
router.get('/products/:id/versions', async (req, res) => {
  const id = Number(req.params.id);
  try {
    const rows = await knex('products_audit').where({ product_id: id }).orderBy('version', 'desc').select('*');
    res.json({ success: true, versions: rows });
  } catch (e:any) { res.status(500).json({ error: 'server_error' }); }
});

// rollback product (replaces current row with payload JSON)
router.post('/products/:id/rollback/:version', async (req, res) => {
  const id = Number(req.params.id);
  const version = Number(req.params.version);
  try {
    const snap = await knex('products_audit').where({ product_id: id, version }).first();
    if (!snap) return res.status(404).json({ error: 'not_found' });
    const payload = snap.payload ? JSON.parse(snap.payload) : null;
    if (!payload) return res.status(500).json({ error: 'invalid_snapshot' });
    await knex('products').where({ id }).update({ ...payload, updated_at: new Date() });
    res.json({ success: true });
  } catch (e:any) { res.status(500).json({ error: 'server_error' }); }
});

export default router;
