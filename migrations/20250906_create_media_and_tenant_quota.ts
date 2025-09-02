import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const hasMedia = await knex.schema.hasTable('media');
  if (!hasMedia) {
    await knex.schema.createTable('media', (t) => {
      t.increments('id').primary();
      t.integer('tenant_id').unsigned().references('id').inTable('tenants').onDelete('CASCADE');
      t.string('path').notNullable();
      t.string('mime').nullable();
      t.bigInteger('size_bytes').notNullable().defaultTo(0);
      t.string('storage_provider').nullable();
      t.timestamp('created_at').defaultTo(knex.fn.now());
    });
  }

  const hasTenants = await knex.schema.hasTable('tenants');
  if (hasTenants) {
    const hasStorage = await knex.schema.hasColumn('tenants', 'storage_quota_bytes');
    if (!hasStorage) {
      await knex.schema.alterTable('tenants', (t) => {
        t.bigInteger('storage_quota_bytes').nullable();
        t.bigInteger('monthly_bandwidth_bytes').nullable();
        t.timestamp('updated_at').defaultTo(knex.fn.now()).alter();
      });
    }
  }
}

export async function down(knex: Knex): Promise<void> {
  const hasMedia = await knex.schema.hasTable('media');
  if (hasMedia) await knex.schema.dropTable('media');
  const hasTenants = await knex.schema.hasTable('tenants');
  if (hasTenants) {
    const hasStorage = await knex.schema.hasColumn('tenants', 'storage_quota_bytes');
    if (hasStorage) {
      await knex.schema.alterTable('tenants', (t) => {
        t.dropColumn('storage_quota_bytes');
        t.dropColumn('monthly_bandwidth_bytes');
      });
    }
  }
}
