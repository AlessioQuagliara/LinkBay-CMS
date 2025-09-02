import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('plugins', (table) => {
    table.increments('id').primary();
    table.string('name').notNullable();
    table.text('description').nullable();
    table.integer('price_cents').notNullable().defaultTo(0);
    table.string('stripe_price_id').nullable();
    table.integer('creator_tenant_id').unsigned().references('id').inTable('tenants').onDelete('SET NULL');
    table.timestamps(true, true);
  });

  await knex.schema.createTable('tenant_plugins', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().references('id').inTable('tenants').onDelete('CASCADE');
    table.integer('plugin_id').unsigned().references('id').inTable('plugins').onDelete('CASCADE');
    table.string('stripe_session_id').nullable();
    table.enu('status', ['pending', 'active', 'cancelled', 'failed']).notNullable().defaultTo('pending');
    table.timestamp('purchased_at').nullable();
    table.timestamps(true, true);
    table.unique(['tenant_id', 'plugin_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('tenant_plugins');
  await knex.schema.dropTableIfExists('plugins');
}
