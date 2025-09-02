import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';

const router = Router();
router.use(requirePermission('admin.view'));

// recent logs (paginated)
router.get('/logs', async (req, res) => {
  const limit = Math.min(200, Number(req.query.limit || 100));
  const offset = Number(req.query.offset || 0);
  try {
    const rows = await (knex as any)('plugin_logs').select('*').orderBy('created_at','desc').limit(limit).offset(offset);
    res.json({ success: true, logs: rows });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

// summary metrics for a plugin
router.get('/metrics/:pluginId', async (req, res) => {
  const pluginId = String(req.params.pluginId);
  try {
    const total = await (knex as any)('plugin_logs').where({ plugin_id: pluginId }).count('* as cnt').first();
    const avgDuration = await (knex as any)('plugin_logs').where({ plugin_id: pluginId }).avg('duration_ms as avg').first();
    const slow = await (knex as any)('plugin_logs').where({ plugin_id: pluginId }).andWhere('duration_ms', '>', 500).count('* as cnt').first();
    res.json({ success: true, metrics: { total: Number(total && total.cnt || 0), avgDuration: Number(avgDuration && avgDuration.avg || 0), slowCount: Number(slow && slow.cnt || 0) } });
  } catch (err:any) { res.status(500).json({ error: 'server_error' }); }
});

export default router;
