import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('users', (table) => {
    table.uuid('id').primary().defaultTo(knex.raw('uuid_generate_v4()'));
    table.uuid('tenant_id').notNullable();
    table.string('email').notNullable();
    table.string('mfa_secret');
    table.string('role').notNullable().defaultTo('member');
    table.timestamp('created_at').notNullable().defaultTo(knex.fn.now());

    table.unique(['tenant_id', 'email']);
    table.foreign('tenant_id').references('id').inTable('tenants').onDelete('CASCADE');
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('users');
}
