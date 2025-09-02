import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // audit_logs created_at index
  await knex.schema.alterTable('audit_logs', (table) => {
    // create index if not exists
    // knex doesn't have conditional create index API, so use raw
  });
  // create indexes only if the target table exists to support non-deterministic migration ordering
  await knex.raw(`
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_logs') THEN
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at)';
      END IF;
      IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pages') THEN
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_pages_slug ON pages (slug)';
      END IF;
    END
    $$;
  `);

  // Replace tenant schema creation function to include indexes for tenant tables
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
      -- indexes for performance
      EXECUTE 'CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders (created_at)';
      EXECUTE 'CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status)';
      EXECUTE 'CREATE INDEX IF NOT EXISTS idx_pages_slug ON pages (slug)';
    END;
    $$ LANGUAGE plpgsql;
  `);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw('DROP INDEX IF EXISTS idx_audit_logs_created_at');
  await knex.raw('DROP INDEX IF EXISTS idx_pages_slug');
  // restore previous create_tenant_schema function if needed - left as no-op
}
