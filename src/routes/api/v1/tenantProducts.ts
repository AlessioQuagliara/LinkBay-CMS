import { Router } from 'express';
import { knex } from '../../../db';
import { requireApiKey, requireScope } from '../../../middleware/requireApiKey';

const router = Router();

// All routes under here require a valid API key
router.use(requireApiKey);

/**
 * GET /api/v1/tenant/products
 * @summary List products for tenant
 * @return {array} 200 - products
 */
router.get('/products', requireScope('products:read'), async (req:any, res) => {
  try {
    const tenantId = req.tenant.id;
    // tenant-specific products assumed to be in tenant schema or have tenant_id
    const products = await knex('products').where('tenant_id', tenantId).select('*').limit(100);
    res.json(products);
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

/**
 * POST /api/v1/tenant/products
 * @summary Create a product
 * @param {object} request.body.required - product body
 */
router.post('/products', requireScope('products:write'), async (req:any, res) => {
  try {
    const tenantId = req.tenant.id;
    const body = req.body || {};
    // minimal validation
    if (!body.name || !body.price_cents) return res.status(400).json({ error: 'name_and_price_required' });
    const [id] = await knex('products').insert({ tenant_id: tenantId, name: body.name, description: body.description || null, price_cents: body.price_cents, created_at: new Date() }).returning('id');
    res.status(201).json({ id });
  } catch (err:any) { console.error('api create product', err); res.status(500).json({ error: 'server_error' }); }
});

export default router;
