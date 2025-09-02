import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const has = await knex.schema.hasColumn('tenants', 'data_residency_region');
  if (!has) {
    await knex.schema.alterTable('tenants', (t) => {
      t.string('data_residency_region', 64).nullable().defaultTo(null).comment('Optional region code where tenant data should reside, e.g. eu-west-1');
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  const has = await knex.schema.hasColumn('tenants', 'data_residency_region');
  if (has) {
    await knex.schema.alterTable('tenants', (t) => {
      t.dropColumn('data_residency_region');
    });
  }
}
