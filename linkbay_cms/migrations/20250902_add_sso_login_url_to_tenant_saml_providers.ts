import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('tenant_saml_providers');
  if (!has) return;
  const hasCol = await knex.schema.hasColumn('tenant_saml_providers', 'sso_login_url');
  if (!hasCol) {
    await knex.schema.alterTable('tenant_saml_providers', (t) => {
      t.text('sso_login_url');
    });
  }
}

export async function down(knex: Knex): Promise<void> {
  const has = await knex.schema.hasTable('tenant_saml_providers');
  if (!has) return;
  const hasCol = await knex.schema.hasColumn('tenant_saml_providers', 'sso_login_url');
  if (hasCol) {
    await knex.schema.alterTable('tenant_saml_providers', (t) => {
      t.dropColumn('sso_login_url');
    });
  }
}
