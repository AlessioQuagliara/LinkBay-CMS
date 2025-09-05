import { Client } from 'pg';
import knex, { Knex } from 'knex';
import config from '../knexfile';

const env = process.env.NODE_ENV || 'development';
const knexConfig = (config as any)[env] as Knex.Config;

async function ensureDatabaseExists(): Promise<void> {
  const { host, port, user, password, database } = knexConfig.connection as any;

  // connect to postgres default db to create target db if missing
  const client = new Client({ host, port, user, password, database: 'postgres' });
  await client.connect();

  const res = await client.query('SELECT 1 FROM pg_database WHERE datname = $1', [database]);
  if (res.rowCount === 0) {
    // create db
    // NOTE: requires the connecting user to have CREATEDB privilege
    await client.query(`CREATE DATABASE "${database}"`);
  }

  await client.end();
}

let db: Knex;

export async function initDb(): Promise<Knex> {
  if (!db) {
    await ensureDatabaseExists();
    db = knex(knexConfig);
  }
  return db;
}

export default function getDb(): Knex {
  if (!db) throw new Error('Database not initialized. Call initDb() first.');
  return db;
}
