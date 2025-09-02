import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('plugin_logs');
  if (!has) {
    await knex.schema.createTable('plugin_logs', (t) => {
      t.bigIncrements('id').primary();
      t.string('plugin_id').notNullable();
      t.integer('tenant_id').nullable();
      t.string('level').notNullable().defaultTo('info');
      t.text('message').notNullable();
      t.jsonb('meta').nullable();
      t.integer('duration_ms').nullable();
      t.timestamp('created_at').defaultTo(knex.fn.now());
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('plugin_logs');
  if (has) await knex.schema.dropTable('plugin_logs');
}
