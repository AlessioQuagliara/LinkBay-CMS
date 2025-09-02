import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('ab_tests', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.string('name').notNullable();
    t.enu('status', ['draft','running','paused']).notNullable().defaultTo('draft');
    t.string('goal_metric').nullable();
    t.jsonb('meta').nullable();
    t.timestamp('created_at').defaultTo(knex.fn.now());
    t.timestamp('updated_at').defaultTo(knex.fn.now());
  });

  await knex.schema.createTable('ab_test_variants', (t) => {
    t.increments('id').primary();
    t.integer('test_id').notNullable().references('id').inTable('ab_tests').onDelete('CASCADE');
    t.string('name').notNullable();
    t.integer('traffic_percentage').notNullable().defaultTo(50);
    t.jsonb('custom_data').nullable();
    t.timestamp('created_at').defaultTo(knex.fn.now());
    t.timestamp('updated_at').defaultTo(knex.fn.now());
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('ab_test_variants');
  await knex.schema.dropTableIfExists('ab_tests');
}
