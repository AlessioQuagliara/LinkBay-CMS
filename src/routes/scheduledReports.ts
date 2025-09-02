import { Router } from 'express';
import { knex } from '../db';
import { requirePermission } from '../middleware/permissions';
import { sendMail } from '../services/mailer';
import analyticsRouter from './analytics';
import ejs from 'ejs';
import fs from 'fs';
import path from 'path';

const router = Router();

// list
router.get('/', requirePermission('reports.view'), async (req:any, res) => {
  const tenant = req.tenant; if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const rows = await knex('scheduled_reports').where({ tenant_id: tenant.id }).select('*');
  res.json({ reports: rows });
});

// create
router.post('/', requirePermission('reports.manage'), async (req:any, res) => {
  const tenant = req.tenant; if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const { frequency, recipient_email, name, options } = req.body;
  const [id] = await knex('scheduled_reports').insert({ tenant_id: tenant.id, frequency, recipient_email, name, options }).returning('id');
  res.json({ id });
});

// delete
router.delete('/:id', requirePermission('reports.manage'), async (req:any, res) => {
  const tenant = req.tenant; if (!tenant) return res.status(404).json({ error: 'tenant_required' });
  const id = Number(req.params.id);
  await knex('scheduled_reports').where({ id, tenant_id: tenant.id }).del();
  res.json({ ok: true });
});

// helper to generate and send a report for a given scheduled report record
export async function runReport(record:any, start:Date, end:Date) {
  const tenantId = record.tenant_id;
  // reuse analytics queries (call the analytics queries directly)
  const analytics = require('./analytics').default;
  // build overview by calling internal functions via analyticsKnex
  const analyticsApi = require('./analytics');
  // We'll call the analytics endpoints programmatically by invoking the functions inside analyticsRouter handlers would be complex; instead run queries similar to analytics.ts
  const analyticsKnex = require('../lib/analyticsConsumer').analyticsKnex;
  const visitsRow:any = await analyticsKnex('analytics.events').where({ tenant_id: tenantId, event_type: 'pageview' }).andWhere('timestamp','>=', start).andWhere('timestamp','<=', end).count('* as cnt').first();
  const visits = Number(visitsRow?.cnt || 0);
  const revenueRes:any = await analyticsKnex.raw(`SELECT COALESCE(SUM((event_data->>'amount_cents')::bigint),0) as revenue FROM analytics.events WHERE tenant_id = ? AND event_type = ? AND timestamp >= ? AND timestamp <= ?`, [tenantId, 'purchasecompleted', start.toISOString(), end.toISOString()]);
  const revenue = Number((revenueRes && revenueRes.rows && revenueRes.rows[0] && revenueRes.rows[0].revenue) || 0);

  // render email template
  const tpl = fs.readFileSync(path.join(__dirname, '..', 'views', 'email', 'report_summary.ejs'), 'utf-8');
  const html = ejs.render(tpl, { visits, revenue_cents: revenue, start, end, tenantId });
  await sendMail({ to: record.recipient_email, subject: `Report ${record.name || ''} (${record.frequency})`, html });
  await knex('scheduled_reports').where({ id: record.id }).update({ last_sent_at: new Date() });
}

export default router;
