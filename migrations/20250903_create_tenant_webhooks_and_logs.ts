import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('tenant_webhooks', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.text('url').notNullable();
    t.string('secret', 200).nullable();
    t.jsonb('event_types').nullable();
    t.boolean('is_active').notNullable().defaultTo(true);
    t.timestamps(true, true);
  });

  await knex.schema.createTable('webhook_logs', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').nullable();
    t.integer('webhook_id').nullable().references('id').inTable('tenant_webhooks').onDelete('SET NULL');
    t.string('event_type').notNullable();
    t.jsonb('event_payload').nullable();
    t.boolean('success').notNullable().defaultTo(false);
    t.integer('attempts').notNullable().defaultTo(0);
    t.text('response_status').nullable();
    t.text('error').nullable();
    t.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('webhook_logs');
  await knex.schema.dropTableIfExists('tenant_webhooks');
}
