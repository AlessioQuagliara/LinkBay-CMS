import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('scheduled_reports', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.enu('frequency', ['daily','weekly']).notNullable().defaultTo('daily');
    t.string('recipient_email').notNullable();
    t.string('name').nullable();
    t.jsonb('options').nullable();
    t.timestamp('last_sent_at').nullable();
    t.timestamp('created_at').defaultTo(knex.fn.now());
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('scheduled_reports');
}
