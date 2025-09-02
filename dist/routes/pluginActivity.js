"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const router = (0, express_1.Router)();
router.use((0, permissions_1.requirePermission)('admin.view'));
// recent logs (paginated)
router.get('/logs', async (req, res) => {
    const limit = Math.min(200, Number(req.query.limit || 100));
    const offset = Number(req.query.offset || 0);
    try {
        const rows = await db_1.knex('plugin_logs').select('*').orderBy('created_at', 'desc').limit(limit).offset(offset);
        res.json({ success: true, logs: rows });
    }
    catch (err) {
        res.status(500).json({ error: 'server_error' });
    }
});
// summary metrics for a plugin
router.get('/metrics/:pluginId', async (req, res) => {
    const pluginId = String(req.params.pluginId);
    try {
        const total = await db_1.knex('plugin_logs').where({ plugin_id: pluginId }).count('* as cnt').first();
        const avgDuration = await db_1.knex('plugin_logs').where({ plugin_id: pluginId }).avg('duration_ms as avg').first();
        const slow = await db_1.knex('plugin_logs').where({ plugin_id: pluginId }).andWhere('duration_ms', '>', 500).count('* as cnt').first();
        res.json({ success: true, metrics: { total: Number(total && total.cnt || 0), avgDuration: Number(avgDuration && avgDuration.avg || 0), slowCount: Number(slow && slow.cnt || 0) } });
    }
    catch (err) {
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
