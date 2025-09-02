import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('audit_logs', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().nullable().references('id').inTable('tenants').onDelete('SET NULL');
    table.integer('user_id').unsigned().nullable();
    table.string('action').notNullable();
    table.string('ip_address').nullable();
    table.string('user_agent').nullable();
    table.jsonb('metadata').nullable();
    table.timestamp('created_at').defaultTo(knex.fn.now());
    table.index(['tenant_id']);
    table.index(['user_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('audit_logs');
}
