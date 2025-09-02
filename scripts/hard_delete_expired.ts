import { knex as createKnex } from 'knex';
import dotenv from 'dotenv';
dotenv.config();

const knex = createKnex({ client: 'pg', connection: process.env.DATABASE_URL });

async function run() {
  // delete users anonymized > 60 days
  const daysUsers = Number(process.env.HARD_DELETE_USERS_DAYS || '60');
  const usersCutoff = new Date(Date.now() - daysUsers * 24 * 60 * 60 * 1000);
  try {
    const deleted = await knex('users').where('anonymized_at', '<', usersCutoff).del();
    console.info('hard deleted users count', deleted);
  } catch (e) { console.error('failed deleting users', e); }

  // delete orders deleted_at > 30 days
  const daysOrders = Number(process.env.HARD_DELETE_ORDERS_DAYS || '30');
  const ordersCutoff = new Date(Date.now() - daysOrders * 24 * 60 * 60 * 1000);
  try {
    const od = await knex('orders').where('deleted_at', '<', ordersCutoff).del();
    console.info('hard deleted orders count', od);
  } catch (e) { console.error('failed deleting orders', e); }

  process.exit(0);
}

run().catch(e=>{ console.error(e); process.exit(1); });
