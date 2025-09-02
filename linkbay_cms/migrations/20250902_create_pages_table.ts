import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('pages', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().references('id').inTable('tenants').onDelete('CASCADE');
    table.string('name').notNullable();
    table.text('content_json').nullable();
    table.text('content_html').nullable();
    table.string('slug').notNullable().unique();
    table.timestamps(true, true);
    table.index(['tenant_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('pages');
}
