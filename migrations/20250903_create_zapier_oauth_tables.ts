import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('zapier_oauth_codes', (t) => {
    t.string('code').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.string('client_id').notNullable();
    t.timestamp('expires_at').notNullable();
    t.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
  });

  await knex.schema.createTable('zapier_oauth_tokens', (t) => {
    t.string('access_token').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.string('client_id').notNullable();
  t.jsonb('scopes').nullable();
    t.timestamp('expires_at').notNullable();
    t.timestamp('created_at').notNullable().defaultTo(knex.fn.now());
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('zapier_oauth_tokens');
  await knex.schema.dropTableIfExists('zapier_oauth_codes');
}
