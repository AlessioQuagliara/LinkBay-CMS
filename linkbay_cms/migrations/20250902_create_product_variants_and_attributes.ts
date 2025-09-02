import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // Create tables in a defensive way: if products table isn't present yet, create product_id column without FK
  await knex.raw(`
    DO $$
    BEGIN
      IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'product_variants') THEN
        CREATE TABLE product_variants (
          id serial PRIMARY KEY,
          product_id integer NOT NULL,
          sku varchar NULL,
          price_cents integer NOT NULL DEFAULT 0,
          stock integer NOT NULL DEFAULT 0,
          created_at timestamptz DEFAULT now(),
          updated_at timestamptz DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS product_variants_product_id_index ON product_variants(product_id);
      END IF;

      IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'variant_attributes') THEN
        CREATE TABLE variant_attributes (
          id serial PRIMARY KEY,
          variant_id integer NOT NULL,
          name varchar NOT NULL,
          value varchar NOT NULL,
          created_at timestamptz DEFAULT now(),
          updated_at timestamptz DEFAULT now()
        );
        CREATE INDEX IF NOT EXISTS variant_attributes_variant_id_index ON variant_attributes(variant_id);
      END IF;

      -- If products table exists, add a foreign key constraint linking variants to products
      IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'products') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name WHERE tc.table_name='product_variants' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='product_id') THEN
          ALTER TABLE product_variants
            ADD CONSTRAINT product_variants_product_id_foreign FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE;
        END IF;
      END IF;

      -- If product_variants exists, ensure variant_attributes FK exists
      IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'product_variants') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints tc JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name WHERE tc.table_name='variant_attributes' AND tc.constraint_type='FOREIGN KEY' AND kcu.column_name='variant_id') THEN
          ALTER TABLE variant_attributes
            ADD CONSTRAINT variant_attributes_variant_id_foreign FOREIGN KEY (variant_id) REFERENCES product_variants(id) ON DELETE CASCADE;
        END IF;
      END IF;
    END
    $$;
  `);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw(`
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='variant_attributes_variant_id_foreign') THEN
        ALTER TABLE variant_attributes DROP CONSTRAINT IF EXISTS variant_attributes_variant_id_foreign;
      END IF;
      IF EXISTS (SELECT 1 FROM information_schema.table_constraints WHERE constraint_name='product_variants_product_id_foreign') THEN
        ALTER TABLE product_variants DROP CONSTRAINT IF EXISTS product_variants_product_id_foreign;
      END IF;
      DROP TABLE IF EXISTS variant_attributes CASCADE;
      DROP TABLE IF EXISTS product_variants CASCADE;
    END
    $$;
  `);
}
