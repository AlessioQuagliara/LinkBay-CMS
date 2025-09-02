"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const audit_1 = require("../middleware/audit");
const router = (0, express_1.Router)();
// List roles (admin only)
router.get('/', (0, permissions_1.requirePermission)('roles.view'), async (req, res) => {
    const tenant = req.tenant;
    const rows = await db_1.knex('roles').where({ tenant_id: tenant ? tenant.id : null }).select('*');
    res.json({ success: true, roles: rows });
});
// Create role
router.post('/', (0, permissions_1.requirePermission)('roles.manage'), async (req, res) => {
    const tenant = req.tenant;
    const { name, permissions } = req.body;
    const [id] = await db_1.knex('roles').insert({ name, tenant_id: tenant ? tenant.id : null }).returning('id');
    if (permissions && Array.isArray(permissions)) {
        for (const p of permissions) {
            // assume permission id passed; in production you'd resolve names
            await db_1.knex('role_permissions').insert({ role_id: id, permission_id: p }).catch(() => { });
        }
    }
    try {
        await (0, audit_1.auditChange)('USER_ROLE_UPDATED', { tenantId: tenant ? tenant.id : undefined, userId: req.user ? req.user.id : undefined, oldValue: null, newValue: { id, name, permissions } });
    }
    catch (e) { }
    res.json({ success: true, id });
});
// Update role (name/permissions)
router.put('/:id', (0, permissions_1.requirePermission)('roles.manage'), async (req, res) => {
    const roleId = Number(req.params.id);
    const { name, permissions } = req.body;
    const before = await db_1.knex('roles').where({ id: roleId }).first();
    await db_1.knex('roles').where({ id: roleId }).update({ name });
    if (permissions && Array.isArray(permissions)) {
        await db_1.knex('role_permissions').where({ role_id: roleId }).del();
        for (const p of permissions) {
            await db_1.knex('role_permissions').insert({ role_id: roleId, permission_id: p }).catch(() => { });
        }
    }
    try {
        await (0, audit_1.auditChange)('USER_ROLE_UPDATED', { tenantId: before ? before.tenant_id : undefined, userId: req.user ? req.user.id : undefined, oldValue: before, newValue: { id: roleId, name, permissions } });
    }
    catch (e) { }
    res.json({ success: true });
});
// Delete role
router.delete('/:id', (0, permissions_1.requirePermission)('roles.manage'), async (req, res) => {
    const roleId = Number(req.params.id);
    const before = await db_1.knex('roles').where({ id: roleId }).first();
    await db_1.knex('role_permissions').where({ role_id: roleId }).del();
    await db_1.knex('roles').where({ id: roleId }).del();
    try {
        await (0, audit_1.auditChange)('USER_ROLE_UPDATED', { tenantId: before ? before.tenant_id : undefined, userId: req.user ? req.user.id : undefined, oldValue: before, newValue: null });
    }
    catch (e) { }
    res.json({ success: true });
});
exports.default = router;
