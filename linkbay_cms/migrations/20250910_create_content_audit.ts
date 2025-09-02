import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // pages audit table
  const hasPages = await knex.schema.hasTable('pages');
  if (hasPages) {
    const hasAudit = await knex.schema.hasTable('pages_audit');
    if (!hasAudit) {
      await knex.schema.createTable('pages_audit', (t) => {
        t.bigIncrements('id').primary();
        t.integer('page_id').notNullable();
        t.integer('tenant_id').nullable();
        t.string('name').nullable();
        t.text('content_json').nullable();
        t.text('content_html').nullable();
        t.string('slug').nullable();
        t.integer('version').notNullable().defaultTo(1);
        t.integer('modified_by').nullable();
        t.timestamp('modified_at').defaultTo(knex.fn.now());
        t.jsonb('metadata').nullable();
      });
    }

    // create trigger function for pages
    await knex.raw(`
      CREATE OR REPLACE FUNCTION pages_audit_before_update() RETURNS trigger AS $$
      DECLARE
        v integer;
      BEGIN
        SELECT COALESCE(MAX(version),0) INTO v FROM pages_audit WHERE page_id = OLD.id;
        INSERT INTO pages_audit(page_id, tenant_id, name, content_json, content_html, slug, version, modified_at)
        VALUES (OLD.id, OLD.tenant_id, OLD.name, OLD.content_json, OLD.content_html, OLD.slug, v + 1, now());
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql;
    `);

    // attach trigger if not exists
    await knex.raw(`
      DO $$
      BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'pages_audit_trigger') THEN
          CREATE TRIGGER pages_audit_trigger BEFORE UPDATE ON pages FOR EACH ROW EXECUTE FUNCTION pages_audit_before_update();
        END IF;
      END$$;
    `);
  }

  // products audit (only if products table exists)
  const hasProducts = await knex.schema.hasTable('products');
  if (hasProducts) {
    const hasProdAudit = await knex.schema.hasTable('products_audit');
    if (!hasProdAudit) {
      await knex.schema.createTable('products_audit', (t) => {
        t.bigIncrements('id').primary();
        t.integer('product_id').notNullable();
        t.integer('tenant_id').nullable();
        t.text('payload').nullable();
        t.integer('version').notNullable().defaultTo(1);
        t.integer('modified_by').nullable();
        t.timestamp('modified_at').defaultTo(knex.fn.now());
      });
    }
    await knex.raw(`
      CREATE OR REPLACE FUNCTION products_audit_before_update() RETURNS trigger AS $$
      DECLARE v integer; rec jsonb; BEGIN
        SELECT COALESCE(MAX(version),0) INTO v FROM products_audit WHERE product_id = OLD.id;
        rec = to_jsonb(OLD);
        INSERT INTO products_audit(product_id, tenant_id, payload, version, modified_at) VALUES (OLD.id, OLD.tenant_id, rec::text, v + 1, now());
        RETURN NEW;
      END; $$ LANGUAGE plpgsql;
    `);
    await knex.raw(`
      DO $$
      BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'products_audit_trigger') THEN
          CREATE TRIGGER products_audit_trigger BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION products_audit_before_update();
        END IF;
      END$$;
    `);
  }
}

export async function down(knex: Knex): Promise<void> {
  // drop triggers and functions if exist, then tables
  try { await knex.raw(`DROP TRIGGER IF EXISTS pages_audit_trigger ON pages`); } catch(e){}
  try { await knex.raw(`DROP FUNCTION IF EXISTS pages_audit_before_update()`); } catch(e){}
  try { await knex.schema.dropTableIfExists('pages_audit'); } catch(e){}

  try { await knex.raw(`DROP TRIGGER IF EXISTS products_audit_trigger ON products`); } catch(e){}
  try { await knex.raw(`DROP FUNCTION IF EXISTS products_audit_before_update()`); } catch(e){}
  try { await knex.schema.dropTableIfExists('products_audit'); } catch(e){}
}
