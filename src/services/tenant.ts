import { knex } from '../db';
import { getTenantDB, buildTenantSchemaName } from '../dbMultiTenant';

export async function createTenantSchema(tenantId: number) {
  const schema = buildTenantSchemaName(tenantId);
  // create schema and run tenant migrations via DB helper function
  await knex.raw(`CREATE SCHEMA IF NOT EXISTS "${schema}"`);
  await knex.raw(`SELECT create_tenant_schema('${schema}')`);
  await knex.raw(`SELECT create_tenant_ecommerce_schema('${schema}')`);
}
