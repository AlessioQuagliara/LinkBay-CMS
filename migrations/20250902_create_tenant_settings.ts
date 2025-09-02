import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('tenant_settings', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    table.string('primary_color', 32).nullable();
    table.string('secondary_color', 32).nullable();
    table.string('logo_url').nullable();
    table.string('favicon_url').nullable();
    table.text('css_overrides').nullable();
    table.enu('default_theme', ['light','dark','auto']).notNullable().defaultTo('light');
    table.timestamps(true, true);
    table.unique(['tenant_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('tenant_settings');
}
