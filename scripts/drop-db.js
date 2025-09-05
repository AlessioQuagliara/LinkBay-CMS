#!/usr/bin/env node
// drops the configured database from .env using pg Client
const dotenv = require('dotenv');
dotenv.config();
const { Client } = require('pg');

const DB_HOST = process.env.DB_HOST || process.env.DB_HOSTNAME || '127.0.0.1';
const DB_PORT = process.env.DB_PORT || '5432';
const DB_USER = process.env.DB_USER || process.env.DB_USERNAME || 'postgres';
const DB_PASSWORD = process.env.DB_PASSWORD || '';
const DB_NAME = process.env.DB_NAME || process.env.DB || process.env.DATABASE || (process.env.DATABASE_URL ? new URL(process.env.DATABASE_URL).pathname.slice(1) : undefined) || 'linkbay_cms_dev';

const conn = { host: DB_HOST, port: Number(DB_PORT), user: DB_USER, password: DB_PASSWORD, database: DB_NAME };

async function drop() {
  const client = new Client({ host: conn.host, port: conn.port, user: conn.user, password: conn.password, database: 'postgres' });
  await client.connect();
  try {
    const dbName = conn.database;
    console.log('Dropping database', dbName);
    await client.query(`DROP DATABASE IF EXISTS "${dbName}"`);
    console.log('Dropped', dbName);
  } catch (err) {
    console.error('Drop failed', err && err.message ? err.message : err);
    process.exit(1);
  } finally {
    await client.end();
  }
}

drop().then(() => process.exit(0));
