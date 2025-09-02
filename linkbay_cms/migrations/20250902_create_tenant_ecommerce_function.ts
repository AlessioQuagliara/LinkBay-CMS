import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.raw(`
    CREATE OR REPLACE FUNCTION create_tenant_ecommerce_schema(schema_name text) RETURNS void AS $$
    BEGIN
      EXECUTE format('SET search_path TO %I, public', schema_name);
      EXECUTE 'CREATE TABLE IF NOT EXISTS products (id serial PRIMARY KEY, name varchar NOT NULL, description text, price numeric(12,2) NOT NULL, stock integer DEFAULT 0, images jsonb, data_json jsonb, created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
      EXECUTE 'CREATE TABLE IF NOT EXISTS carts (id serial PRIMARY KEY, user_id integer, session_id varchar, status varchar NOT NULL DEFAULT ''active'', created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
      EXECUTE 'CREATE TABLE IF NOT EXISTS cart_items (id serial PRIMARY KEY, cart_id integer NOT NULL, product_id integer NOT NULL, quantity integer NOT NULL DEFAULT 1, created_at timestamptz DEFAULT now(), updated_at timestamptz DEFAULT now())';
      EXECUTE 'CREATE INDEX IF NOT EXISTS idx_cart_items_cart_id ON cart_items(cart_id)';
    END;
    $$ LANGUAGE plpgsql;
  `);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw('DROP FUNCTION IF EXISTS create_tenant_ecommerce_schema(text)');
}
