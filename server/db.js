const path = require('path');
const knex = require('knex');

const connection = process.env.DATABASE_URL || process.env.DB_URL || process.env.DB_CONNECTION || 'postgres://root:root@127.0.0.1:5432/linkbay_dev';

const db = knex({
  client: 'pg',
  connection,
  migrations: {
    directory: path.join(__dirname, 'migrations'),
  },
  seeds: {
    directory: path.join(__dirname, 'seeds'),
  },
});

module.exports = db;
