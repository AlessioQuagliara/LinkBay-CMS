import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';
import { auditChange } from '../middleware/audit';

const router = Router();

// List roles (admin only)
router.get('/', requirePermission('roles.view'), async (req, res) => {
  const tenant = (req as any).tenant;
  const rows = await (knex as any)('roles').where({ tenant_id: tenant ? tenant.id : null }).select('*');
  res.json({ success: true, roles: rows });
});

// Create role
router.post('/', requirePermission('roles.manage'), async (req, res) => {
  const tenant = (req as any).tenant;
  const { name, permissions } = req.body;
  const [id] = await (knex as any)('roles').insert({ name, tenant_id: tenant ? tenant.id : null }).returning('id');
  if (permissions && Array.isArray(permissions)) {
    for (const p of permissions) {
      // assume permission id passed; in production you'd resolve names
      await (knex as any)('role_permissions').insert({ role_id: id, permission_id: p }).catch(()=>{});
    }
  }
  try { await auditChange('USER_ROLE_UPDATED', { tenantId: tenant ? tenant.id : undefined, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: null, newValue: { id, name, permissions } }); } catch(e){}
  res.json({ success: true, id });
});

// Update role (name/permissions)
router.put('/:id', requirePermission('roles.manage'), async (req, res) => {
  const roleId = Number(req.params.id);
  const { name, permissions } = req.body;
  const before = await (knex as any)('roles').where({ id: roleId }).first();
  await (knex as any)('roles').where({ id: roleId }).update({ name });
  if (permissions && Array.isArray(permissions)) {
    await (knex as any)('role_permissions').where({ role_id: roleId }).del();
    for (const p of permissions) {
      await (knex as any)('role_permissions').insert({ role_id: roleId, permission_id: p }).catch(()=>{});
    }
  }
  try { await auditChange('USER_ROLE_UPDATED', { tenantId: before ? before.tenant_id : undefined, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: before, newValue: { id: roleId, name, permissions } }); } catch(e){}
  res.json({ success: true });
});

// Delete role
router.delete('/:id', requirePermission('roles.manage'), async (req, res) => {
  const roleId = Number(req.params.id);
  const before = await (knex as any)('roles').where({ id: roleId }).first();
  await (knex as any)('role_permissions').where({ role_id: roleId }).del();
  await (knex as any)('roles').where({ id: roleId }).del();
  try { await auditChange('USER_ROLE_UPDATED', { tenantId: before ? before.tenant_id : undefined, userId: (req as any).user ? (req as any).user.id : undefined, oldValue: before, newValue: null }); } catch(e){}
  res.json({ success: true });
});

export default router;
