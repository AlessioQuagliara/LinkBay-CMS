import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.raw(`
    CREATE OR REPLACE FUNCTION create_tenant_conversations_schema(schema_name text) RETURNS void AS $$
    BEGIN
      EXECUTE format('SET search_path TO %I, public', schema_name);
      EXECUTE 'CREATE TABLE IF NOT EXISTS conversations (id serial PRIMARY KEY, subject varchar NOT NULL, status varchar NOT NULL DEFAULT ''open'', created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
      EXECUTE 'CREATE TABLE IF NOT EXISTS messages (id serial PRIMARY KEY, conversation_id integer NOT NULL, user_id integer NOT NULL, body text NOT NULL, created_at timestamptz DEFAULT now())';
      EXECUTE 'CREATE TABLE IF NOT EXISTS conversation_participants (id serial PRIMARY KEY, conversation_id integer NOT NULL, user_id integer NOT NULL, role varchar DEFAULT ''participant'', created_at timestamptz DEFAULT now())';
    END;
    $$ LANGUAGE plpgsql;
  `);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw('DROP FUNCTION IF EXISTS create_tenant_conversations_schema(text)');
}
