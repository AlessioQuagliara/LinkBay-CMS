import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.raw(`
    CREATE OR REPLACE FUNCTION create_tenant_schema(schema_name text) RETURNS void AS $$
    BEGIN
      EXECUTE format('CREATE SCHEMA IF NOT EXISTS "%I"', schema_name);
      EXECUTE format('SET search_path TO %I, public', schema_name);
      -- create products
      EXECUTE 'CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY, sku varchar NOT NULL, title varchar NOT NULL, price_cents integer NOT NULL, meta json, created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
      -- create orders
      EXECUTE 'CREATE TABLE IF NOT EXISTS orders (id serial PRIMARY KEY, customer_id integer NOT NULL, items json NOT NULL, total_cents integer NOT NULL, status varchar NOT NULL DEFAULT ''pending'', created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
      -- create pages
      EXECUTE 'CREATE TABLE IF NOT EXISTS pages (id serial PRIMARY KEY, slug varchar NOT NULL, body text, created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
    END;
    $$ LANGUAGE plpgsql;
  `);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw('DROP FUNCTION IF EXISTS create_tenant_schema(text)');
}
