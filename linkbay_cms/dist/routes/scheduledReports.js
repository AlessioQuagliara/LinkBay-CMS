"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.runReport = runReport;
const express_1 = require("express");
const db_1 = require("../db");
const permissions_1 = require("../middleware/permissions");
const mailer_1 = require("../services/mailer");
const ejs_1 = __importDefault(require("ejs"));
const fs_1 = __importDefault(require("fs"));
const path_1 = __importDefault(require("path"));
const router = (0, express_1.Router)();
// list
router.get('/', (0, permissions_1.requirePermission)('reports.view'), async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const rows = await (0, db_1.knex)('scheduled_reports').where({ tenant_id: tenant.id }).select('*');
    res.json({ reports: rows });
});
// create
router.post('/', (0, permissions_1.requirePermission)('reports.manage'), async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const { frequency, recipient_email, name, options } = req.body;
    const [id] = await (0, db_1.knex)('scheduled_reports').insert({ tenant_id: tenant.id, frequency, recipient_email, name, options }).returning('id');
    res.json({ id });
});
// delete
router.delete('/:id', (0, permissions_1.requirePermission)('reports.manage'), async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const id = Number(req.params.id);
    await (0, db_1.knex)('scheduled_reports').where({ id, tenant_id: tenant.id }).del();
    res.json({ ok: true });
});
// helper to generate and send a report for a given scheduled report record
async function runReport(record, start, end) {
    const tenantId = record.tenant_id;
    // reuse analytics queries (call the analytics queries directly)
    const analytics = require('./analytics').default;
    // build overview by calling internal functions via analyticsKnex
    const analyticsApi = require('./analytics');
    // We'll call the analytics endpoints programmatically by invoking the functions inside analyticsRouter handlers would be complex; instead run queries similar to analytics.ts
    const analyticsKnex = require('../lib/analyticsConsumer').analyticsKnex;
    const visitsRow = await analyticsKnex('analytics.events').where({ tenant_id: tenantId, event_type: 'pageview' }).andWhere('timestamp', '>=', start).andWhere('timestamp', '<=', end).count('* as cnt').first();
    const visits = Number(visitsRow?.cnt || 0);
    const revenueRes = await analyticsKnex.raw(`SELECT COALESCE(SUM((event_data->>'amount_cents')::bigint),0) as revenue FROM analytics.events WHERE tenant_id = ? AND event_type = ? AND timestamp >= ? AND timestamp <= ?`, [tenantId, 'purchasecompleted', start.toISOString(), end.toISOString()]);
    const revenue = Number((revenueRes && revenueRes.rows && revenueRes.rows[0] && revenueRes.rows[0].revenue) || 0);
    // render email template
    const tpl = fs_1.default.readFileSync(path_1.default.join(__dirname, '..', 'views', 'email', 'report_summary.ejs'), 'utf-8');
    const html = ejs_1.default.render(tpl, { visits, revenue_cents: revenue, start, end, tenantId });
    await (0, mailer_1.sendMail)({ to: record.recipient_email, subject: `Report ${record.name || ''} (${record.frequency})`, html });
    await (0, db_1.knex)('scheduled_reports').where({ id: record.id }).update({ last_sent_at: new Date() });
}
exports.default = router;
