"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const router = (0, express_1.Router)({ mergeParams: true });
// Get roles for a user
router.get('/:userId/roles', (0, permissions_1.requirePermission)('roles.view'), async (req, res) => {
    const userId = Number(req.params.userId);
    const rows = await db_1.knex('user_roles').where({ user_id: userId }).select('*');
    res.json({ success: true, roles: rows });
});
// Assign roles to a user
router.post('/:userId/roles', (0, permissions_1.requirePermission)('roles.manage'), async (req, res) => {
    const userId = Number(req.params.userId);
    const { roleIds } = req.body;
    if (!Array.isArray(roleIds))
        return res.status(400).json({ error: 'invalid' });
    // remove existing and add new
    await db_1.knex('user_roles').where({ user_id: userId }).del();
    for (const r of roleIds) {
        await db_1.knex('user_roles').insert({ user_id: userId, role_id: r }).catch(() => { });
    }
    res.json({ success: true });
});
exports.default = router;
