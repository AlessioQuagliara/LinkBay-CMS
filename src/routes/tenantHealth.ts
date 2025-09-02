import { Router } from 'express';
import { knex } from '../db';
import { analyticsKnex } from '../lib/analyticsConsumer';
import { jwtAuth } from '../middleware/jwtAuth';
import { requirePermission } from '../middleware/permissions';

const router = Router();

// protect tenant health endpoints: require auth + admin.view
router.use(jwtAuth);
router.use(requirePermission('admin.view'));

router.get('/', async (req:any, res) => {
  const tenant = req.tenant;
  if (!tenant) return res.status(404).json({ error: 'tenant_required' });

  try {
    // recent orders by status (last 24h)
    const tenantDb = (await import('../dbMultiTenant')).getTenantDB(tenant.id);
    const recentOrders = await tenantDb('orders').where('created_at', '>=', new Date(Date.now()-24*3600*1000)).select('status');
    const orderCounts: any = { pending: 0, problematic: 0 };
    recentOrders.forEach((o:any)=>{
      if (o.status === 'pending') orderCounts.pending++;
      if (['failed','cancelled','error'].includes(o.status)) orderCounts.problematic++;
    });

    // page performance (avg load time ms last 7 days)
    const perfRes: any = await analyticsKnex.raw(`
      SELECT AVG((event_data->>'load_time_ms')::numeric) as avg_load_ms, COUNT(*) as cnt
      FROM analytics.events
      WHERE tenant_id = ? AND event_type IN ('pageperf','pageload','page_performance') AND timestamp >= now() - interval '7 days'
    `, [tenant.id]);
    const perfRow = perfRes && perfRes.rows && perfRes.rows[0] ? perfRes.rows[0] : null;
    const avg_load_ms = perfRow ? Number(perfRow.avg_load_ms || 0) : null;

    // subscription status
    const tenantRow = await knex('tenants').where({ id: tenant.id }).first();
    const subscription = { status: tenantRow && tenantRow.subscription_status ? tenantRow.subscription_status : 'none', expires_at: tenantRow && tenantRow.subscription_expires_at ? tenantRow.subscription_expires_at : null };

    // recent errors
    const errors = await analyticsKnex('analytics.events').where({ tenant_id: tenant.id }).andWhere(function(this:any){ this.where('event_type','error').orWhere('event_type','server_error').orWhere('event_type','exception'); }).orderBy('timestamp','desc').limit(20).select('event_type','event_data','timestamp');

    res.json({ orders: orderCounts, performance: { avg_load_ms, samples: perfRow ? Number(perfRow.cnt||0) : 0 }, subscription, recent_errors: errors });
  } catch (err:any) {
    console.error('tenant health error', err && err.message);
    res.status(500).json({ error: 'server_error' });
  }
});

export default router;
