import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // Create separate schema for analytics to avoid polluting operational schema
  await knex.raw('CREATE SCHEMA IF NOT EXISTS analytics');

  // events table stores raw analytic events
  await knex.schema.withSchema('analytics').createTable('events', (t) => {
    t.bigIncrements('id').primary();
    t.integer('tenant_id').notNullable();
    t.string('event_type', 128).notNullable();
    t.jsonb('event_data').nullable();
    t.integer('user_id').nullable();
    t.string('session_id', 128).nullable();
    t.text('url_path').nullable();
    t.timestamp('timestamp', { useTz: true }).notNullable().defaultTo(knex.fn.now());
    t.timestamp('created_at', { useTz: true }).notNullable().defaultTo(knex.fn.now());
    // indexes for fast tenant-scoped queries
    t.index(['tenant_id'], 'analytics_events_tenant_idx');
    t.index(['event_type'], 'analytics_events_type_idx');
    t.index(['timestamp'], 'analytics_events_timestamp_idx');
    t.index(['tenant_id', 'timestamp'], 'analytics_events_tenant_timestamp_idx');
  });

  // sessions table to track session metadata and attribution
  await knex.schema.withSchema('analytics').createTable('sessions', (t) => {
    t.string('session_id', 128).primary();
    t.integer('tenant_id').notNullable();
    t.integer('user_id').nullable();
    t.timestamp('started_at', { useTz: true }).notNullable().defaultTo(knex.fn.now());
    t.timestamp('ended_at', { useTz: true }).nullable();
    t.string('utm_source', 256).nullable();
    t.string('device_type', 128).nullable();
    t.jsonb('meta').nullable();
    t.index(['tenant_id'], 'analytics_sessions_tenant_idx');
    t.index(['started_at'], 'analytics_sessions_started_idx');
  });
}

export async function down(knex: Knex): Promise<void> {
  // drop schema cascade to remove tables as well
  await knex.raw('DROP SCHEMA IF EXISTS analytics CASCADE');
}
