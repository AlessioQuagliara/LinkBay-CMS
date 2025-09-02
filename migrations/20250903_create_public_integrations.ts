import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('public_integrations', (t) => {
    t.increments('id').primary();
    t.string('name').notNullable();
    t.text('description').nullable();
    t.string('logo_url').nullable();
    t.boolean('is_active').notNullable().defaultTo(true);
    t.jsonb('config_schema').nullable();
    t.timestamps(true, true);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('public_integrations');
}
