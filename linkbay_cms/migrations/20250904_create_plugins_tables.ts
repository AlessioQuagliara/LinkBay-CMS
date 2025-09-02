import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // available plugins registry
  const hasAvailable = await knex.schema.hasTable('available_plugins');
  if (!hasAvailable) {
    await knex.schema.createTable('available_plugins', (t) => {
      t.string('id').primary();
      t.string('name').notNullable();
      t.text('description').nullable();
      t.string('latest_version').nullable();
      t.boolean('is_core').defaultTo(false);
      t.boolean('is_approved').defaultTo(false);
      t.timestamp('created_at').defaultTo(knex.fn.now());
      t.timestamp('updated_at').defaultTo(knex.fn.now());
    });
  }

  const hasTenant = await knex.schema.hasTable('tenant_plugins');
  if (!hasTenant) {
    await knex.schema.createTable('tenant_plugins', (t) => {
      t.increments('id').primary();
      t.integer('tenant_id').notNullable();
      t.string('plugin_id').notNullable();
      t.string('version').nullable();
      t.boolean('is_active').defaultTo(false);
      t.jsonb('config').nullable();
      t.timestamp('created_at').defaultTo(knex.fn.now());
      t.timestamp('updated_at').defaultTo(knex.fn.now());
      t.unique(['tenant_id', 'plugin_id']);
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  const hasTenant = await knex.schema.hasTable('tenant_plugins');
  if (hasTenant) await knex.schema.dropTable('tenant_plugins');
  const hasAvailable = await knex.schema.hasTable('available_plugins');
  if (hasAvailable) await knex.schema.dropTable('available_plugins');
}
