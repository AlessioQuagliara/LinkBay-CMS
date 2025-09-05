import { Knex } from 'knex';

export async function seed(knex: Knex): Promise<void> {
  // clear tables (if needed) - keep truncate order according to FKs
  await knex('user_providers').del().catch(() => {});
  await knex('users').del().catch(() => {});
  await knex('tenants').del().catch(() => {});

  const [tenant] = await knex('tenants').insert({ name: 'Example Agency' }).returning('*');

  const [user] = await knex('users')
    .insert({ tenant_id: tenant.id, email: 'admin@example.com', role: 'owner' })
    .returning('*');

  // no providers yet; MFA will be configured separately
  console.log('Seeded tenant:', tenant.id, 'admin user:', user.id);
}
