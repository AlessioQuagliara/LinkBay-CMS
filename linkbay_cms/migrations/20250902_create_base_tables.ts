import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('tenants', (table) => {
    table.increments('id').primary();
    table.string('name').notNullable();
    table.string('subdomain').notNullable().unique();
    table.string('status').notNullable().defaultTo('active');
    table.string('stripe_connect_id').nullable();
    table.string('paypal_merchant_id').nullable();
    table.timestamps(true, true);
  });

  await knex.schema.createTable('users', (table) => {
    table.increments('id').primary();
    table.integer('tenant_id').unsigned().references('id').inTable('tenants').onDelete('CASCADE');
    table.string('email').notNullable();
    table.string('password_hash').notNullable();
    table.enu('role', ['super_admin', 'tenant_admin', 'user', 'agency']).notNullable().defaultTo('user');
    table.boolean('email_verified').notNullable().defaultTo(false);
    table.timestamps(true, true);
    table.unique(['tenant_id', 'email']);
    table.index(['tenant_id']);
  });

  await knex.schema.createTable('refresh_tokens', (table) => {
    table.increments('id').primary();
    table.integer('user_id').unsigned().references('id').inTable('users').onDelete('CASCADE');
    table.string('token').notNullable().unique();
    table.timestamp('expires_at').notNullable();
    table.timestamps(true, true);
    table.index(['user_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('refresh_tokens');
  await knex.schema.dropTableIfExists('users');
  await knex.schema.dropTableIfExists('tenants');
}
