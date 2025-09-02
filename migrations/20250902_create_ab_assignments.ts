import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.raw('CREATE SCHEMA IF NOT EXISTS analytics');
  await knex.schema.withSchema('analytics').createTable('ab_assignments', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').notNullable();
    t.integer('test_id').notNullable();
    t.integer('variant_id').notNullable();
    t.string('session_id', 128).nullable();
    t.integer('user_id').nullable();
    t.timestamp('assigned_at').defaultTo(knex.fn.now());
    t.unique(['test_id','session_id']);
    t.index(['tenant_id','test_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.withSchema('analytics').dropTableIfExists('ab_assignments');
}
