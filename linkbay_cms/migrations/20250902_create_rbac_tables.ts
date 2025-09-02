import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('permissions', (table) => {
    table.increments('id').primary();
    table.string('name').notNullable().unique();
    table.text('description').nullable();
    table.timestamps(true, true);
  });

  await knex.schema.createTable('roles', (table) => {
    table.increments('id').primary();
    table.string('name').notNullable();
    table.integer('tenant_id').unsigned().nullable().references('id').inTable('tenants').onDelete('CASCADE');
    table.timestamps(true, true);
    table.unique(['name', 'tenant_id']);
  });

  await knex.schema.createTable('role_permissions', (table) => {
    table.increments('id').primary();
    table.integer('role_id').unsigned().references('id').inTable('roles').onDelete('CASCADE');
    table.integer('permission_id').unsigned().references('id').inTable('permissions').onDelete('CASCADE');
    table.unique(['role_id', 'permission_id']);
  });

  await knex.schema.createTable('user_roles', (table) => {
    table.increments('id').primary();
    table.integer('user_id').unsigned().references('id').inTable('users').onDelete('CASCADE');
    table.integer('role_id').unsigned().references('id').inTable('roles').onDelete('CASCADE');
    table.unique(['user_id', 'role_id']);
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('user_roles');
  await knex.schema.dropTableIfExists('role_permissions');
  await knex.schema.dropTableIfExists('roles');
  await knex.schema.dropTableIfExists('permissions');
}
