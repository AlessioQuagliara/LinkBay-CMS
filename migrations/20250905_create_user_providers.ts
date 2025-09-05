import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.schema.createTable('user_providers', (table) => {
    table.uuid('id').primary().defaultTo(knex.raw('uuid_generate_v4()'));
    table.uuid('user_id').notNullable();
    table.string('provider').notNullable();
    table.string('provider_id').notNullable();
    table.text('access_token');
    table.timestamp('created_at').notNullable().defaultTo(knex.fn.now());

    table.unique(['provider', 'provider_id']);
    table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE');
  });
}

export async function down(knex: Knex): Promise<void> {
  await knex.schema.dropTableIfExists('user_providers');
}
