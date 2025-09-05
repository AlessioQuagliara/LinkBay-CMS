#!/usr/bin/env node
require('dotenv').config();
const { Client } = require('pg');
const { spawn } = require('child_process');
const path = require('path');

const DB_HOST = process.env.DB_HOST || '127.0.0.1';
const DB_PORT = process.env.DB_PORT || '5432';
const DB_USER = process.env.DB_USER || 'postgres';
const DB_PASSWORD = process.env.DB_PASSWORD || '';
const DB_NAME = process.env.DB_NAME || 'linkbay_cms_dev';

async function ensureDatabase() {
  const client = new Client({ host: DB_HOST, port: Number(DB_PORT), user: DB_USER, password: DB_PASSWORD, database: 'postgres' });
  try {
    await client.connect();
    const res = await client.query('SELECT 1 FROM pg_database WHERE datname = $1', [DB_NAME]);
    if (res.rowCount === 0) {
      console.log(`Database ${DB_NAME} not found. Creating...`);
      await client.query(`CREATE DATABASE "${DB_NAME}"`);
      console.log(`Database ${DB_NAME} created.`);
    } else {
      console.log(`Database ${DB_NAME} already exists.`);
    }
  } finally {
    await client.end();
  }
}

function runKnex(args) {
  return new Promise((resolve, reject) => {
    const knexCli = path.join('node_modules', '.bin', 'knex');
    const cmd = process.platform === 'win32' ? `${knexCli}.cmd` : knexCli;
    const child = spawn(cmd, args, { stdio: 'inherit', shell: false });
    child.on('exit', (code) => {
      if (code === 0) resolve(); else reject(new Error(`knex exited with code ${code}`));
    });
    child.on('error', reject);
  });
}

async function main() {
  try {
    await ensureDatabase();

    console.log('Running knex migrations...');
    await runKnex(['--knexfile', path.join(process.cwd(), 'knexfile.ts'), 'migrate:latest', '--env', process.env.NODE_ENV || 'development']);

    console.log('Running knex seeds...');
    await runKnex(['--knexfile', path.join(process.cwd(), 'knexfile.ts'), 'seed:run', '--env', process.env.NODE_ENV || 'development']);

    console.log('Database initialized successfully.');
    process.exit(0);
  } catch (err) {
    console.error('Failed to initialize database:', err.message || err);
    process.exit(1);
  }
}

main();
