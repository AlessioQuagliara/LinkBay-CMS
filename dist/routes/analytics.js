"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const analyticsConsumer_1 = require("../lib/analyticsConsumer");
const router = (0, express_1.Router)();
function parseRange(q) {
    const start = q.startDate ? new Date(String(q.startDate)) : new Date(Date.now() - 7 * 24 * 3600 * 1000);
    const end = q.endDate ? new Date(String(q.endDate)) : new Date();
    return { start, end };
}
// GET /api/analytics/overview
router.get('/overview', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { start, end } = parseRange(req.query);
    try {
        const visitsRow = await (0, analyticsConsumer_1.analyticsKnex)('analytics.events').where({ tenant_id: tenant.id, event_type: 'pageview' }).andWhere('timestamp', '>=', start).andWhere('timestamp', '<=', end).count('* as cnt').first();
        const visits = Number(visitsRow?.cnt || 0);
        const uniqueRow = await (0, analyticsConsumer_1.analyticsKnex)('analytics.events').where({ tenant_id: tenant.id }).andWhere('timestamp', '>=', start).andWhere('timestamp', '<=', end).whereNotNull('user_id').countDistinct('user_id as cnt').first();
        const uniqueUsers = Number(uniqueRow?.cnt || 0);
        const purchasesRow = await (0, analyticsConsumer_1.analyticsKnex)('analytics.events').where({ tenant_id: tenant.id, event_type: 'purchasecompleted' }).andWhere('timestamp', '>=', start).andWhere('timestamp', '<=', end).count('* as cnt').first();
        const purchases = Number(purchasesRow?.cnt || 0);
        // revenue: sum event_data->>'amount_cents'
        const revenueRes = await analyticsConsumer_1.analyticsKnex.raw(`SELECT COALESCE(SUM((event_data->>'amount_cents')::bigint),0) as revenue FROM analytics.events WHERE tenant_id = ? AND event_type = ? AND timestamp >= ? AND timestamp <= ?`, [tenant.id, 'purchasecompleted', start.toISOString(), end.toISOString()]);
        const revenue = Number((revenueRes && revenueRes.rows && revenueRes.rows[0] && revenueRes.rows[0].revenue) || 0);
        const conversion = visits > 0 ? (purchases / visits) : 0;
        res.json({ visits, uniqueUsers, purchases, revenue_cents: revenue, conversion_rate: conversion });
    }
    catch (err) {
        console.error('analytics overview error', err && err.message);
        res.status(500).json({ error: 'server_error' });
    }
});
// GET /api/analytics/popular-pages
router.get('/popular-pages', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { start, end } = parseRange(req.query);
    try {
        const rows = await (0, analyticsConsumer_1.analyticsKnex)('analytics.events')
            .select('url_path')
            .count('* as cnt')
            .where({ tenant_id: tenant.id, event_type: 'pageview' })
            .andWhere('timestamp', '>=', start)
            .andWhere('timestamp', '<=', end)
            .groupBy('url_path')
            .orderBy('cnt', 'desc')
            .limit(50);
        res.json({ pages: rows.map((r) => ({ url: r.url_path, views: Number(r.cnt) })) });
    }
    catch (err) {
        console.error('popular-pages error', err && err.message);
        res.status(500).json({ error: 'server_error' });
    }
});
// GET /api/analytics/sales
router.get('/sales', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { start, end } = parseRange(req.query);
    try {
        const rows = await analyticsConsumer_1.analyticsKnex.raw(`
      SELECT date_trunc('day', timestamp) as day, COALESCE(SUM((event_data->>'amount_cents')::bigint),0) as revenue_cents, COUNT(*) as orders
      FROM analytics.events
      WHERE tenant_id = ? AND event_type = ? AND timestamp >= ? AND timestamp <= ?
      GROUP BY day
      ORDER BY day ASC
    `, [tenant.id, 'purchasecompleted', start.toISOString(), end.toISOString()]);
        const series = (rows && rows.rows) ? rows.rows.map((r) => ({ day: r.day, revenue_cents: Number(r.revenue_cents), orders: Number(r.orders) })) : [];
        res.json({ series });
    }
    catch (err) {
        console.error('sales error', err && err.message);
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
