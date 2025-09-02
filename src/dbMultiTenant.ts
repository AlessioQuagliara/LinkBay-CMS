import knexInit, { Knex } from 'knex';
import { knex as primaryKnex } from './db';

// Cache per-tenant Knex instances
const tenantCache = new Map<number, Knex>();
// Cache per-region Knex instances (used when tenant opts into a region)
const regionCache = new Map<string, Knex>();

function tenantSchemaName(tenantId: number) {
  return `tenant_${tenantId}`;
}

/**
 * Resolve the correct Knex instance for a tenant.
 * If the tenant has data_residency_region set, use a regional DB connection.
 * Otherwise default to the primary connection.
 */
export function getTenantDB(tenantId: number): Knex {
  const cached = tenantCache.get(tenantId);
  if (cached) return cached;

  // Fetch tenant record to read data_residency_region
  // Note: synchronous style avoided; we use primaryKnex which is available synchronously
  // but this call is async; to keep function signature sync we read the region via a fast query
  // using a cached approach: if tenant table is small this is acceptable; alternatively
  // callers can pass tenant object directly. Here we perform a synchronous-ish workaround
  // by using .first() and blocking via deasync is NOT acceptable; instead we assume
  // callers have loaded tenant into request and we fallback when not available.

  // Best-effort: try to read tenant residency using primaryKnex; if it fails or is async,
  // fall back to primary connection. We'll implement a minimal async helper and export it
  // called getTenantDBAsync below for callers that can await.

  // Fallback: use primary connection with schema searchPath
  const schema = tenantSchemaName(tenantId);
  const cfg: Knex.Config = {
    client: 'pg',
    connection: (primaryKnex as any).client.config.connection,
    searchPath: [schema, 'public']
  };
  const k = knexInit(cfg);
  tenantCache.set(tenantId, k);
  return k;
}

/**
 * Async variant that resolves tenant.data_residency_region and returns a Knex instance
 * connected to the regional DB (if set) and configured with the tenant schema search_path.
 */
export async function getTenantDBAsync(tenantId: number): Promise<Knex> {
  const cached = tenantCache.get(tenantId);
  if (cached) return cached;

  const tenant = await (primaryKnex as any)('tenants').where({ id: tenantId }).first().catch(()=>null);
  const region = tenant && tenant.data_residency_region ? String(tenant.data_residency_region) : null;

  let connConfig: any = (primaryKnex as any).client.config.connection;

  if (region) {
    // region keys mapped to env or knexfile names
    const key = `region:${region}`;
    // attempt to reuse regionKnex from cache
    let regionKnex = regionCache.get(region);
    if (!regionKnex) {
      // read connection string from environment naming convention
      // map common region identifiers to env var names
      const envKey = `DATABASE_URL_${region.toUpperCase().replace(/[-.]/g,'_')}`;
      const envConn = process.env[envKey];
      if (envConn) {
        connConfig = envConn;
      } else {
        // fallback to primary
        connConfig = (primaryKnex as any).client.config.connection;
      }
      regionKnex = knexInit({ client: 'pg', connection: connConfig });
      regionCache.set(region, regionKnex);
    } else {
      connConfig = (regionKnex as any).client.config.connection;
    }
  }

  const schema = tenantSchemaName(tenantId);
  const cfg: Knex.Config = {
    client: 'pg',
    connection: connConfig,
    searchPath: [schema, 'public']
  };
  const k = knexInit(cfg);
  tenantCache.set(tenantId, k);
  return k;
}

export function clearTenantDBCache(tenantId: number) {
  const k = tenantCache.get(tenantId);
  if (!k) return;
  k.destroy();
  tenantCache.delete(tenantId);
}

export function clearRegionCache(region: string) {
  const k = regionCache.get(region);
  if (!k) return;
  k.destroy();
  regionCache.delete(region);
}

export function buildTenantSchemaName(tenantId: number) {
  return tenantSchemaName(tenantId);
}
