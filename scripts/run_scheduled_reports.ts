#!/usr/bin/env ts-node
import dotenv from 'dotenv'; dotenv.config();
import knexInit from 'knex';
import path from 'path';
const knex = knexInit({ client: 'pg', connection: process.env.DATABASE_URL });

async function main(){
  const rows = await knex('scheduled_reports').select('*');
  for (const r of rows) {
    const freq = r.frequency || 'daily';
    let start = new Date(); let end = new Date();
    end.setHours(23,59,59,999);
    if (freq === 'daily') {
      start = new Date(); start.setDate(start.getDate()-1); start.setHours(0,0,0,0);
    } else {
      // weekly: previous 7 days
      start = new Date(); start.setDate(start.getDate()-7); start.setHours(0,0,0,0);
    }
    // import runner
    const runner = require('../src/routes/scheduledReports').runReport;
    try { await runner(r, start, end); console.log('sent report', r.id); } catch (e) { console.error('report failed', r.id, e); }
  }
  process.exit(0);
}

main().catch(e=>{ console.error(e); process.exit(1); });
