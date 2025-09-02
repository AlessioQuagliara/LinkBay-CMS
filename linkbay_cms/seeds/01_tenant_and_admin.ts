import bcrypt from 'bcryptjs';

export async function seed(knex: any): Promise<void> {
  // clear
  await knex('refresh_tokens').del().catch(()=>{});
  await knex('users').del().catch(()=>{});
  await knex('tenants').del().catch(()=>{});

  const [tenantId] = await knex('tenants').insert({ name: 'Default Tenant', subdomain: 'default' }).returning('id');
  const hash = await bcrypt.hash('SuperSecret1!', 10);
  await knex('users').insert({ tenant_id: tenantId, email: 'admin@linkbay.local', password_hash: hash, role: 'super_admin', email_verified: true });
}
