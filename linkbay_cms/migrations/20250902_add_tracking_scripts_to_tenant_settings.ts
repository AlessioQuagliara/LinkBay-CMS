import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.alterTable('tenant_settings', (t) => {
    t.text('tracking_scripts').nullable();
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.alterTable('tenant_settings', (t) => {
    t.dropColumn('tracking_scripts');
  });
}
