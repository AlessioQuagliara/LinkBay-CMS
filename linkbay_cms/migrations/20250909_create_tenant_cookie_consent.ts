import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('tenant_cookie_consent');
  if (!has) {
    await knex.schema.createTable('tenant_cookie_consent', (t) => {
      t.increments('id').primary();
      t.integer('tenant_id').unsigned().notNullable().unique();
      t.text('banner_text').nullable();
      t.jsonb('necessary_cookies').nullable();
      t.jsonb('analytics_cookies').nullable();
      t.jsonb('marketing_cookies').nullable();
      t.boolean('enabled').defaultTo(true);
      t.timestamp('created_at').defaultTo(knex.fn.now());
      t.timestamp('updated_at').defaultTo(knex.fn.now());
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('tenant_cookie_consent');
  if (has) await knex.schema.dropTable('tenant_cookie_consent');
}
