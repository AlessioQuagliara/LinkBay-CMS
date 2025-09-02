import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.alterTable('tenants', (table) => {
    table.integer('subscription_plan_id').unsigned().nullable();
    table.string('billing_cycle').notNullable().defaultTo('monthly');
    table.string('subscription_status').notNullable().defaultTo('inactive');
    table.timestamp('subscription_expires_at').nullable();
  });

  await knex.schema.createTable('invoices', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().references('id').inTable('tenants').onDelete('CASCADE');
    table.string('stripe_invoice_id').nullable().unique();
    table.integer('amount_cents').notNullable().defaultTo(0);
    table.string('currency').notNullable().defaultTo('usd');
    table.string('status').notNullable().defaultTo('pending');
    table.timestamp('period_start').nullable();
    table.timestamp('period_end').nullable();
    table.timestamp('paid_at').nullable();
    table.jsonb('metadata').nullable();
    table.timestamps(true, true);
    table.index(['tenant_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('invoices');
  await knex.schema.alterTable('tenants', (table) => {
    table.dropColumn('subscription_plan_id');
    table.dropColumn('billing_cycle');
    table.dropColumn('subscription_status');
    table.dropColumn('subscription_expires_at');
  });
}
