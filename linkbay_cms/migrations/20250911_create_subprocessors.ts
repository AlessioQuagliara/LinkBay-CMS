import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const exists = await knex.schema.hasTable('subprocessors');
  if (exists) return;
  await knex.schema.createTable('subprocessors', (t) => {
    t.increments('id').primary();
    t.string('name', 200).notNullable();
    t.string('purpose', 200).notNullable();
    t.jsonb('data_centers').notNullable().defaultTo(JSON.stringify([]));
    t.text('notes').nullable();
    t.boolean('is_active').notNullable().defaultTo(true);
    t.timestamp('created_at').defaultTo(knex.fn.now());
    t.timestamp('updated_at').nullable();
  });
}

export async function down(knex: Knex): Promise<void> {
  const exists = await knex.schema.hasTable('subprocessors');
  if (exists) await knex.schema.dropTable('subprocessors');
}
