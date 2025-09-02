import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  await knex.raw(`
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'pages') THEN
        ALTER TABLE pages ADD COLUMN IF NOT EXISTS language varchar(8) NOT NULL DEFAULT 'en';
        EXECUTE 'CREATE INDEX IF NOT EXISTS idx_pages_tenant_id_language ON pages (tenant_id, language)';
      END IF;
    END
    $$;
  `);
}

export async function down(knex: Knex): Promise<void> {
  await knex.raw(`
    DO $$
    BEGIN
      IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'pages' AND column_name = 'language') THEN
        ALTER TABLE pages DROP COLUMN IF EXISTS language;
        EXECUTE 'DROP INDEX IF EXISTS idx_pages_tenant_id_language';
      END IF;
    END
    $$;
  `);
}
