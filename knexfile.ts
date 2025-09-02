import type { Knex } from 'knex';
import dotenv from 'dotenv';
dotenv.config();

// Define per-region connection strings via environment variables, for example:
// DATABASE_URL=postgres://...        -> default
// DATABASE_URL_EU_WEST_1=postgres://...  -> eu-west-1
// DATABASE_URL_US_EAST_1=postgres://...  -> us-east-1
const config: { [key: string]: Knex.Config } = {
  development: {
    client: 'pg',
    connection: process.env.DATABASE_URL || 'postgres://root:root@127.0.0.1:5432/linkbay_dev',
    migrations: { directory: './migrations' },
    seeds: { directory: './seeds' }
  },
  // named connections for regions used by the app to resolve tenant DBs
  'region:eu-west-1': {
    client: 'pg',
    connection: process.env.DATABASE_URL_EU_WEST_1 || process.env.DATABASE_URL || 'postgres://root:root@127.0.0.1:5432/linkbay_eu',
    migrations: { directory: './migrations' }
  },
  'region:us-east-1': {
    client: 'pg',
    connection: process.env.DATABASE_URL_US_EAST_1 || process.env.DATABASE_URL || 'postgres://root:root@127.0.0.1:5432/linkbay_us',
    migrations: { directory: './migrations' }
  }
};

export default config;
