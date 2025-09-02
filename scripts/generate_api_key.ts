import crypto from 'crypto';
import { knex } from '../src/db';

async function run(){
  const tenantId = process.argv[2];
  const name = process.argv[3] || 'script-generated';
  if (!tenantId){ console.error('usage: node generate_api_key.js <tenantId> [name]'); process.exit(2); }
  const raw = crypto.randomBytes(32).toString('hex');
  const hash = crypto.createHash('sha256').update(raw).digest('hex');
  const defaultScopes = ['products:read','products:write','orders:read','orders:write'];
  await knex('api_keys').insert({ tenant_id: Number(tenantId), key_hash: hash, name, scopes: JSON.stringify(defaultScopes), created_at: new Date() });
  console.log('API key for tenant', tenantId, ':', raw);
  process.exit(0);
}

run().catch(err=>{ console.error(err); process.exit(1); });
