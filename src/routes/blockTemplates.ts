import { Router } from 'express';
import { knex } from '../db';

const router = Router();

// List templates: query param `public=true` to get global public templates
router.get('/', async (req, res) => {
  const isPublic = req.query.public === 'true';
  const tenant = (req as any).tenant;
  const q = knex('block_templates').select('id','tenant_id','name','preview_image_url','category','is_public','created_at');
  if(isPublic) q.where('is_public', true).whereNull('tenant_id');
  else if(tenant && tenant.id) q.where(function(){ this.where('tenant_id', tenant.id).orWhere('is_public', true).orWhereNull('tenant_id'); });
  const rows = await q.orderBy('created_at','desc');
  res.json(rows);
});

// Create template (tenant must exist for tenant-specific templates)
router.post('/', async (req, res) => {
  const tenant = (req as any).tenant;
  const { name, preview_image_url, content_json, category, is_public } = req.body;
  if(!name || !content_json) return res.status(400).json({ error: 'invalid_payload' });
  const insert = {
    tenant_id: tenant?.id || null,
    name,
    preview_image_url: preview_image_url || null,
    content_json: typeof content_json === 'string' ? content_json : JSON.stringify(content_json),
    category: category || null,
    is_public: !!is_public
  };
  const [id] = await knex('block_templates').insert(insert).returning('id');
  res.json({ id });
});

export default router;
