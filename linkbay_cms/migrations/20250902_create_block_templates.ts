import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('block_templates', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().nullable().references('id').inTable('tenants').onDelete('CASCADE');
    table.string('name').notNullable();
    table.string('preview_image_url').nullable();
    table.text('content_json').notNullable();
    table.string('category').nullable();
    table.boolean('is_public').notNullable().defaultTo(false);
    table.timestamps(true, true);
    table.unique(['tenant_id', 'name']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('block_templates');
}
