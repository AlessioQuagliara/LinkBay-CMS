import { Router } from 'express';
import { getTenantDB } from '../dbMultiTenant';
import cache, { cacheKeyForQuery } from '../cache';
import eventBus from '../lib/eventBus';

const router = Router();

// Helper to load products with variants (for a given subset)
async function loadProductsWithVariants(k: any, productRows: any[]) {
  const productIds = productRows.map((p:any)=>p.id);
  const variants = productIds.length ? await k('product_variants').whereIn('product_id', productIds).select('*') : [];
  const attributes = variants.length ? await k('variant_attributes').whereIn('variant_id', variants.map((v:any)=>v.id)).select('*') : [];
  const variantsByProduct: any = {};
  variants.forEach((v:any)=>{ variantsByProduct[v.product_id] = variantsByProduct[v.product_id] || []; variantsByProduct[v.product_id].push(v); });
  const attributesByVariant: any = {};
  attributes.forEach((a:any)=>{ attributesByVariant[a.variant_id] = attributesByVariant[a.variant_id] || []; attributesByVariant[a.variant_id].push(a); });
  return productRows.map((p:any)=>({ ...p, variants: (variantsByProduct[p.id]||[]).map((v:any)=>({ ...v, attributes: attributesByVariant[v.id]||[] })) }));
}

// GET /api/products
// Supports JSON (default) and HTMX partial rendering with ?partial=table&page=N
router.get('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const k = (req as any).getTenantDB ? await (req as any).getTenantDB() : getTenantDB(tenant.id);

  // HTMX table partial + pagination
  if (req.query.partial === 'table') {
    const page = Math.max(1, Number(req.query.page) || 1);
    const perPage = Math.max(10, Number(req.query.per_page) || 20);
    const offset = (page - 1) * perPage;
    const [products, countRow] = await Promise.all([
      k('products').select('*').limit(perPage).offset(offset),
      k('products').count('* as cnt').first()
    ]);
    const total = Number(countRow && countRow.cnt || 0);
    const nextPage = offset + products.length < total;
    const rows = await loadProductsWithVariants(k, products);
    // if first page, render full table wrapper, else render just rows to append
    if (page === 1) return res.render('products/partials/table', { rows, page, perPage, nextPage });
    return res.render('products/partials/rows', { rows, page, perPage, nextPage });
  }

  // default JSON API (cached)
  const key = cacheKeyForQuery(tenant.id, 'products:all:with_variants');
  const rows = await cache.cached(key, async () => {
    const products = await k('products').select('*');
    return await loadProductsWithVariants(k, products);
  }, 120);
  res.json(rows);
});

// GET /api/products/new?partial=form - returns form partial
router.get('/new', async (req, res) => {
  if (req.query.partial === 'form') return res.render('partials/product-form', { product: null });
  res.status(400).json({ error: 'bad_request' });
});

// GET /api/products/:id?partial=row - return a single row partial or json
router.get('/:id', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const k = (req as any).getTenantDB ? await (req as any).getTenantDB() : getTenantDB(tenant.id);
  const id = Number(req.params.id);
  const product = await k('products').where({ id }).first();
  if (!product) return res.status(404).json({ error: 'not_found' });
  if (req.query.partial === 'row') {
    const rows = await loadProductsWithVariants(k, [product]);
    return res.render('products/partials/row', { p: rows[0] });
  }
  res.json(product);
});

// DELETE /api/products/:id - support HTMX delete
router.delete('/:id', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const k = (req as any).getTenantDB ? await (req as any).getTenantDB() : getTenantDB(tenant.id);
  const id = Number(req.params.id);
  await k('product_variants').where({ product_id: id }).del();
  await k('products').where({ id }).del();
  // return HTMX snippet to refresh table
  return res.send('<div class="p-2 text-sm text-green-800 bg-green-50 rounded">Prodotto eliminato</div><script>htmx.trigger(document.querySelector(\"#products-table\"), \"refresh\")</script>');
});

// product detail
router.get('/:id', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const k = (req as any).getTenantDB ? await (req as any).getTenantDB() : getTenantDB(tenant.id);
  const id = Number(req.params.id);
  const product = await k('products').where({ id }).first();
  if (!product) return res.status(404).json({ error: 'not_found' });
  // fetch variants
  const variants = await k('product_variants').where({ product_id: id }).select('*');
  try { eventBus.emit({ type: 'ProductViewed', tenant_id: tenant.id, product_id: id, user_id: (req as any).user ? (req as any).user.id : null, timestamp: new Date().toISOString() }); } catch(e){}
  res.json({ ...product, variants });
});

export default router;

