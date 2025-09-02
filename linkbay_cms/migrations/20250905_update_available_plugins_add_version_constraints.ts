import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('available_plugins');
  if (!has) return;
  const hasMin = await knex.schema.hasColumn('available_plugins', 'min_core_version');
  if (!hasMin) {
    await knex.schema.alterTable('available_plugins', (t) => {
      t.string('min_core_version').nullable();
      t.string('max_core_version').nullable();
      t.jsonb('dependencies').nullable();
      t.timestamp('updated_at').defaultTo(knex.fn.now()).alter();
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('available_plugins');
  if (!has) return;
  const hasMin = await knex.schema.hasColumn('available_plugins', 'min_core_version');
  if (hasMin) {
    await knex.schema.alterTable('available_plugins', (t) => {
      t.dropColumn('min_core_version');
      t.dropColumn('max_core_version');
      t.dropColumn('dependencies');
    });
  }
}
