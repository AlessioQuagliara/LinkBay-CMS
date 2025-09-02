"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const analyticsConsumer_1 = require("../lib/analyticsConsumer");
const jwtAuth_1 = require("../middleware/jwtAuth");
const permissions_1 = require("../middleware/permissions");
const router = (0, express_1.Router)();
// protect tenant health endpoints: require auth + admin.view
router.use(jwtAuth_1.jwtAuth);
router.use((0, permissions_1.requirePermission)('admin.view'));
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    try {
        // recent orders by status (last 24h)
        const tenantDb = (await Promise.resolve().then(() => __importStar(require('../dbMultiTenant')))).getTenantDB(tenant.id);
        const recentOrders = await tenantDb('orders').where('created_at', '>=', new Date(Date.now() - 24 * 3600 * 1000)).select('status');
        const orderCounts = { pending: 0, problematic: 0 };
        recentOrders.forEach((o) => {
            if (o.status === 'pending')
                orderCounts.pending++;
            if (['failed', 'cancelled', 'error'].includes(o.status))
                orderCounts.problematic++;
        });
        // page performance (avg load time ms last 7 days)
        const perfRes = await analyticsConsumer_1.analyticsKnex.raw(`
      SELECT AVG((event_data->>'load_time_ms')::numeric) as avg_load_ms, COUNT(*) as cnt
      FROM analytics.events
      WHERE tenant_id = ? AND event_type IN ('pageperf','pageload','page_performance') AND timestamp >= now() - interval '7 days'
    `, [tenant.id]);
        const perfRow = perfRes && perfRes.rows && perfRes.rows[0] ? perfRes.rows[0] : null;
        const avg_load_ms = perfRow ? Number(perfRow.avg_load_ms || 0) : null;
        // subscription status
        const tenantRow = await (0, db_1.knex)('tenants').where({ id: tenant.id }).first();
        const subscription = { status: tenantRow && tenantRow.subscription_status ? tenantRow.subscription_status : 'none', expires_at: tenantRow && tenantRow.subscription_expires_at ? tenantRow.subscription_expires_at : null };
        // recent errors
        const errors = await (0, analyticsConsumer_1.analyticsKnex)('analytics.events').where({ tenant_id: tenant.id }).andWhere(function () { this.where('event_type', 'error').orWhere('event_type', 'server_error').orWhere('event_type', 'exception'); }).orderBy('timestamp', 'desc').limit(20).select('event_type', 'event_data', 'timestamp');
        res.json({ orders: orderCounts, performance: { avg_load_ms, samples: perfRow ? Number(perfRow.cnt || 0) : 0 }, subscription, recent_errors: errors });
    }
    catch (err) {
        console.error('tenant health error', err && err.message);
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
