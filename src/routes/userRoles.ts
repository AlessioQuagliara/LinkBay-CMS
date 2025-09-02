import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';

const router = Router({ mergeParams: true });

// Get roles for a user
router.get('/:userId/roles', requirePermission('roles.view'), async (req, res) => {
  const userId = Number(req.params.userId);
  const rows = await (knex as any)('user_roles').where({ user_id: userId }).select('*');
  res.json({ success: true, roles: rows });
});

// Assign roles to a user
router.post('/:userId/roles', requirePermission('roles.manage'), async (req, res) => {
  const userId = Number(req.params.userId);
  const { roleIds } = req.body;
  if (!Array.isArray(roleIds)) return res.status(400).json({ error: 'invalid' });
  // remove existing and add new
  await (knex as any)('user_roles').where({ user_id: userId }).del();
  for (const r of roleIds) {
    await (knex as any)('user_roles').insert({ user_id: userId, role_id: r }).catch(()=>{});
  }
  res.json({ success: true });
});

export default router;
