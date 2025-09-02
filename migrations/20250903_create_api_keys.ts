import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('api_keys', (t) => {
    t.increments('id').primary();
    t.integer('tenant_id').notNullable().references('id').inTable('tenants').onDelete('CASCADE');
    t.string('key_hash', 200).notNullable();
    t.string('name').notNullable();
  t.jsonb('scopes').nullable();
    t.timestamp('expires_at').nullable();
    t.timestamps(true, true);
    t.unique(['tenant_id','name']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('api_keys');
}
