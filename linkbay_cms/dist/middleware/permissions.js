"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.requirePermission = requirePermission;
const db_1 = require("../db");
function requirePermission(permissionName) {
    return async (req, res, next) => {
        const user = req.user;
        if (!user)
            return res.status(401).json({ error: 'authentication_required' });
        const tenantId = user.tenant_id;
        try {
            // join user_roles -> roles -> role_permissions -> permissions
            const rows = await db_1.knex('user_roles')
                .join('roles', 'user_roles.role_id', 'roles.id')
                .join('role_permissions', 'roles.id', 'role_permissions.role_id')
                .join('permissions', 'role_permissions.permission_id', 'permissions.id')
                .where('user_roles.user_id', user.id)
                .andWhere(function () { this.whereNull('roles.tenant_id').orWhere('roles.tenant_id', tenantId); })
                .andWhere('permissions.name', permissionName)
                .select('permissions.*');
            if (!rows || rows.length === 0)
                return res.status(403).json({ error: 'forbidden' });
            next();
        }
        catch (err) {
            console.error('permission check failed', err && err.message);
            res.status(500).json({ error: 'server_error' });
        }
    };
}
