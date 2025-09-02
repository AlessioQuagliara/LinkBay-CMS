import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  const hasUsers = await knex.schema.hasTable('users');
  if (hasUsers) {
    const hasDeleted = await knex.schema.hasColumn('users', 'deleted_at');
    const hasAnonymized = await knex.schema.hasColumn('users', 'anonymized_at');
    if (!hasDeleted || !hasAnonymized) {
      await knex.schema.alterTable('users', (t) => {
        if (!hasDeleted) t.timestamp('deleted_at').nullable();
        if (!hasAnonymized) t.timestamp('anonymized_at').nullable();
      });
    }
  }

  const hasOrders = await knex.schema.hasTable('orders');
  if (hasOrders) {
    const hasOrderDeleted = await knex.schema.hasColumn('orders', 'deleted_at');
    if (!hasOrderDeleted) {
      await knex.schema.alterTable('orders', (t) => { t.timestamp('deleted_at').nullable(); });
    }
  }
}

export async function down(knex: Knex): Promise<void> {
  const hasUsers = await knex.schema.hasTable('users');
  if (hasUsers) {
    const hasDeleted = await knex.schema.hasColumn('users', 'deleted_at');
    const hasAnonymized = await knex.schema.hasColumn('users', 'anonymized_at');
    if (hasDeleted || hasAnonymized) {
      await knex.schema.alterTable('users', (t) => {
        if (hasDeleted) t.dropColumn('deleted_at');
        if (hasAnonymized) t.dropColumn('anonymized_at');
      });
    }
  }

  const hasOrders = await knex.schema.hasTable('orders');
  if (hasOrders) {
    const hasOrderDeleted = await knex.schema.hasColumn('orders', 'deleted_at');
    if (hasOrderDeleted) await knex.schema.alterTable('orders', (t) => t.dropColumn('deleted_at'));
  }
}
