import { knex } from '../src/db';
import dotenv from 'dotenv';
dotenv.config();

async function getRetentionDays(key: string, tenantId?: number) {
  try {
    if (tenantId) {
      const row = await knex('retention_policies').where({ tenant_id: tenantId, key }).first();
      if (row) return Number(row.value_days);
    }
    const global = await knex('retention_policies').where({ tenant_id: null, key }).first();
    return global ? Number(global.value_days) : null;
  } catch (e) {
    return null;
  }
}

async function run() {
  console.log('Retention cleanup started', new Date().toISOString());
  // tables to process with corresponding policy keys
  const targets: Array<{ table: string, dateColumn: string, policyKey: string, tenantScoped?: boolean, anonymizeInsteadOfDelete?: boolean }> = [
    { table: 'audit_logs', dateColumn: 'created_at', policyKey: 'audit_logs_retention_days', tenantScoped: false },
    { table: 'user_activity_logs', dateColumn: 'created_at', policyKey: 'user_activity_logs_retention_days', tenantScoped: true },
    // Add more tables here
  ];

  for (const t of targets) {
    if (t.tenantScoped) {
      // process per tenant
      const tenants = await knex('tenants').select('id');
      for (const tenant of tenants) {
        const days = await getRetentionDays(t.policyKey, tenant.id);
        if (!days || days <= 0) continue;
        const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
        const deleted = await knex(t.table).where(t.dateColumn, '<', cutoff).andWhere({ tenant_id: tenant.id }).del().catch(()=>0);
        console.log(`Deleted ${deleted} rows from ${t.table} for tenant ${tenant.id} older than ${days} days`);
      }
    } else {
      const days = await getRetentionDays(t.policyKey, undefined as any);
      if (!days || days <= 0) continue;
      const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000);
      const deleted = await knex(t.table).where(t.dateColumn, '<', cutoff).del().catch(()=>0);
      console.log(`Deleted ${deleted} rows from ${t.table} older than ${days} days`);
    }
  }

  // Special handling: orders -> anonymize instead of delete (example)
  const ordersPolicyDays = await getRetentionDays('orders_retention_days');
  if (ordersPolicyDays && ordersPolicyDays > 0) {
    const cutoff = new Date(Date.now() - ordersPolicyDays * 24 * 60 * 60 * 1000);
    const rows = await knex('orders').where('created_at', '<', cutoff).select('id');
    for (const r of rows) {
      // anonymize: this should call the same anonymization logic used elsewhere; minimal placeholder here
      await knex('orders').where({ id: r.id }).update({ customer_name: '[Redacted]', customer_email: null, anonymized_at: new Date() }).catch(()=>{});
    }
    console.log(`Anonymized ${rows.length} orders older than ${ordersPolicyDays} days`);
  }

  console.log('Retention cleanup finished', new Date().toISOString());
}

if (require.main === module) {
  run().then(()=>process.exit(0)).catch((err)=>{ console.error('cleanup failed', err); process.exit(2); });
}

export default run;
