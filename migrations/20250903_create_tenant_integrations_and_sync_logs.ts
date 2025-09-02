import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('tenant_integrations', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.string('provider').notNullable();
    t.string('client_id').nullable();
    t.string('client_secret').nullable();
    t.text('access_token').nullable();
    t.text('refresh_token').nullable();
    t.timestamp('expires_at').nullable();
    t.jsonb('config').nullable();
    t.boolean('is_active').notNullable().defaultTo(false);
    t.timestamps(true, true);
  });

  await knex.schema.createTable('integration_mappings', (t) => {
    t.increments('id').primary();
    t.integer('integration_id').notNullable().references('id').inTable('tenant_integrations').onDelete('CASCADE');
    t.string('entity').notNullable();
    t.jsonb('mappings').nullable();
    t.timestamps(true, true);
  });

  await knex.schema.createTable('sync_logs', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').nullable();
    t.integer('integration_id').nullable().references('id').inTable('tenant_integrations').onDelete('SET NULL');
    t.string('direction').notNullable(); // 'pull'|'push'
    t.string('entity').notNullable();
    t.string('status').notNullable();
    t.jsonb('details').nullable();
    t.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('sync_logs');
  await knex.schema.dropTableIfExists('integration_mappings');
  await knex.schema.dropTableIfExists('tenant_integrations');
}
