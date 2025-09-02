import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';
import { auditChange } from '../middleware/audit';

const router = Router();

// quick guard: require 'admin.view' permission (super_admin should have it)
router.use(requirePermission('admin.view'));

// list tenants
router.get('/tenants', async (req, res) => {
  try {
    const tenants = await (knex as any)('tenants').select('*').orderBy('id', 'asc');
    res.json({ success: true, tenants });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// toggle tenant status
router.post('/tenants/:id/toggle', async (req, res) => {
  const id = Number(req.params.id);
  try {
    const t = await (knex as any)('tenants').where({ id }).first();
    if (!t) return res.status(404).json({ error: 'not_found' });
    const newStatus = t.status === 'active' ? 'suspended' : 'active';
    await (knex as any)('tenants').where({ id }).update({ status: newStatus, updated_at: new Date() });
    res.json({ success: true, status: newStatus });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// orders metrics
router.get('/orders', async (req, res) => {
  const status = req.query.status || 'paid';
  try {
    const rows = await (knex as any)('orders').where({ status }).select('id','tenant_id','total_cents','created_at').orderBy('created_at','desc').limit(200);
    res.json({ success: true, orders: rows });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// stats
router.get('/stats', async (req, res) => {
  try {
    const totalTenants = await (knex as any)('tenants').count('* as cnt').first();
    const totalUsers = await (knex as any)('users').count('* as cnt').first();
    const today = new Date();
    const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const ordersToday = await (knex as any)('orders').where('created_at', '>=', todayStart).count('* as cnt').first();
    res.json({ success: true, totals: { tenants: Number(totalTenants.cnt||0), users: Number(totalUsers.cnt||0), orders_today: Number(ordersToday.cnt||0) } });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// render admin menus UI page
router.get('/menus', async (req, res) => {
  try {
    // render EJS admin page - view will fetch data via API
  res.render('admin_menus', { user: (req as any).user, t: (req as any).t || ((k: string)=>k) });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// -- Plugin Registry Approval Endpoints
// List available plugins in registry
router.get('/plugins', async (req, res) => {
  try {
    const rows = await (knex as any)('available_plugins').select('*').orderBy('created_at','desc');
    res.json({ success: true, plugins: rows });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// Approve a plugin (admin only)
router.post('/plugins/:id/approve', async (req, res) => {
  const id = String(req.params.id);
  try {
    const row = await (knex as any)('available_plugins').where({ id }).first();
    if (!row) return res.status(404).json({ error: 'not_found' });
    await (knex as any)('available_plugins').where({ id }).update({ is_approved: true, updated_at: new Date() });
  try { await auditChange('PLUGIN_APPROVED', { tenantId: undefined, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: row, newValue: { ...row, is_approved: true } }); } catch(e){}
    res.json({ success: true });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// Revoke approval
router.post('/plugins/:id/revoke', async (req, res) => {
  const id = String(req.params.id);
  try {
    const row = await (knex as any)('available_plugins').where({ id }).first();
    if (!row) return res.status(404).json({ error: 'not_found' });
    await (knex as any)('available_plugins').where({ id }).update({ is_approved: false, updated_at: new Date() });
    // also deactivate any tenant plugin installs for safety
    await (knex as any)('tenant_plugins').where({ plugin_id: id }).update({ is_active: false });
  try { await auditChange('PLUGIN_REVOKED', { tenantId: undefined, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: row, newValue: { ...row, is_approved: false } }); } catch(e){}
    res.json({ success: true });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

export default router;
