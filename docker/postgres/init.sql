-- LinkBay CMS - PostgreSQL initialization
-- The central database is created via POSTGRES_DB env var.
-- Tenant schemas are created automatically by stancl/tenancy PostgreSQLSchemaManager.

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE linkbay_central TO postgres;

-- Enable pg_trgm for better text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
