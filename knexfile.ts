import type { Knex } from 'knex';

const { DB_HOST = '127.0.0.1', DB_PORT = '5432', DB_USER = 'postgres', DB_PASSWORD = '', DB_NAME = 'linkbay_cms_dev' } = process.env;

const connection = {
  host: DB_HOST,
  port: Number(DB_PORT),
  user: DB_USER,
  password: DB_PASSWORD,
  database: DB_NAME,
};

const config: { [key: string]: Knex.Config } = {
  development: {
    client: 'pg',
    connection,
    pool: { min: 2, max: 10 },
    migrations: {
      directory: './migrations',
      extension: 'ts',
    },
    seeds: {
      directory: './seeds',
      extension: 'ts',
    },
  },
};

export default config;
