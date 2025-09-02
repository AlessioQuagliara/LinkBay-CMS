import { execSync } from 'child_process';
import path from 'path';
import knexInit from 'knex';

const knexfile = require('../../knexfile').default;
const config = knexfile.development;

export async function setupTestDb() {
  // expect DATABASE_URL to be pointing to a test database
  const knex = knexInit(config as any);
  await knex.migrate.rollback(undefined, true);
  await knex.migrate.latest();
  await knex.seed.run();
  return knex;
}

export async function teardownTestDb(knex:any) {
  await knex.migrate.rollback(undefined, true);
  await knex.destroy();
}
