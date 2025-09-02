import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const exists = await knex.schema.hasTable('retention_policies');
  if (exists) return;
  await knex.schema.createTable('retention_policies', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').nullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.string('key', 200).notNullable();
    t.integer('value_days').notNullable();
    t.timestamp('created_at').defaultTo(knex.fn.now());
    t.unique(['tenant_id','key']);
  });

  // insert global defaults
  await knex('retention_policies').insert([
    { tenant_id: null, key: 'audit_logs_retention_days', value_days: 365 },
    { tenant_id: null, key: 'user_activity_logs_retention_days', value_days: 90 }
  ]).catch(()=>{});
}

export async function down(knex: Knex): Promise<void> {
  const exists = await knex.schema.hasTable('retention_policies');
  if (exists) await knex.schema.dropTable('retention_policies');
}
