import { Router } from 'express';
import { getTenantDB } from '../dbMultiTenant';
import eventBus from '../lib/eventBus';

const router = Router();

// Add item to cart (create cart if needed)
router.post('/items', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { session_id, user_id, product_id, variant_id, quantity } = req.body;
  const k = (req as any).getTenantDB ? await (req as any).getTenantDB() : getTenantDB(tenant.id);
  // find or create cart
  let cart = await k('carts').where({ session_id }).first();
  if (!cart) {
    const [id] = await k('carts').insert({ session_id, user_id, status: 'active' }).returning('id');
    cart = { id };
  }
  await k('cart_items').insert({ cart_id: cart.id, product_id, variant_id: variant_id || null, quantity });
  try {
    eventBus.emit({ type: 'AddToCart', tenant_id: tenant.id, product_id, variant_id: variant_id || null, quantity: quantity || 1, user_id: user_id || null, session_id: session_id || null, timestamp: new Date().toISOString() });
  } catch(e) {}
  res.json({ ok: true, cart_id: cart.id });
});

// Get cart by session_id
router.get('/', async (req, res) => {
  const tenant = (req as any).tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { session_id } = req.query;
  const k = (req as any).getTenantDB ? await (req as any).getTenantDB() : getTenantDB(tenant.id);
  const cart = await k('carts').where({ session_id }).first();
  if (!cart) return res.json({ items: [] });
  const items = await k('cart_items').where({ cart_id: cart.id }).select('*');
  res.json({ cart, items });
});

export default router;
