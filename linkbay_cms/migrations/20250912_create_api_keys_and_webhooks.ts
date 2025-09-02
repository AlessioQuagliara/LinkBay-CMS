import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // Create api_keys only if it doesn't already exist
  const hasApiKeys = await knex.schema.hasTable('api_keys');
  if (!hasApiKeys) {
    await knex.schema.createTable('api_keys', (t) => {
      t.increments('id').primary();
      t.integer('tenant_id').notNullable().index();
      t.string('name').notNullable();
      t.string('key_hash').notNullable();
      t.string('key_masked').notNullable();
      t.timestamp('created_at').defaultTo(knex.fn.now());
    });
  }

  // Create webhooks only if it doesn't already exist
  const hasWebhooks = await knex.schema.hasTable('webhooks');
  if (!hasWebhooks) {
    await knex.schema.createTable('webhooks', (t) => {
      t.increments('id').primary();
      t.integer('tenant_id').notNullable().index();
      t.string('url').notNullable();
      t.string('events').notNullable();
      t.boolean('active').defaultTo(true);
      t.timestamp('created_at').defaultTo(knex.fn.now());
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('webhooks');
  await knex.schema.dropTableIfExists('api_keys');
}
