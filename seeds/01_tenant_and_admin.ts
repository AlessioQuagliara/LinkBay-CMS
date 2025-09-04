import bcrypt from 'bcryptjs';

export async function seed(knex: any): Promise<void> {
  // clear
  await knex('refresh_tokens').del().catch(()=>{});
  await knex('users').del().catch(()=>{});
  await knex('tenants').del().catch(()=>{});

  const inserted = await knex('tenants').insert({ name: 'Default Tenant', subdomain: 'default' }).returning('id');
  // knex/pg may return [{id: 1}] or [1] depending on config; normalize
  let tenantId: any;
  if (Array.isArray(inserted)) {
    tenantId = inserted[0] && typeof inserted[0] === 'object' ? (inserted[0].id || Object.values(inserted[0])[0]) : inserted[0];
  } else {
    tenantId = inserted && (inserted.id || Object.values(inserted)[0]);
  }
  const hash = await bcrypt.hash('SuperSecret1!', 10);
  await knex('users').insert({ tenant_id: tenantId, email: 'admin@linkbay.local', password_hash: hash, role: 'super_admin', email_verified: true });
}
