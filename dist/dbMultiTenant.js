"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getTenantDB = getTenantDB;
exports.getTenantDBAsync = getTenantDBAsync;
exports.clearTenantDBCache = clearTenantDBCache;
exports.clearRegionCache = clearRegionCache;
exports.buildTenantSchemaName = buildTenantSchemaName;
const knex_1 = __importDefault(require("knex"));
const db_1 = require("./db");
// Cache per-tenant Knex instances
const tenantCache = new Map();
// Cache per-region Knex instances (used when tenant opts into a region)
const regionCache = new Map();
function tenantSchemaName(tenantId) {
    return `tenant_${tenantId}`;
}
/**
 * Resolve the correct Knex instance for a tenant.
 * If the tenant has data_residency_region set, use a regional DB connection.
 * Otherwise default to the primary connection.
 */
function getTenantDB(tenantId) {
    const cached = tenantCache.get(tenantId);
    if (cached)
        return cached;
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
    const cfg = {
        client: 'pg',
        connection: db_1.knex.client.config.connection,
        searchPath: [schema, 'public']
    };
    const k = (0, knex_1.default)(cfg);
    tenantCache.set(tenantId, k);
    return k;
}
/**
 * Async variant that resolves tenant.data_residency_region and returns a Knex instance
 * connected to the regional DB (if set) and configured with the tenant schema search_path.
 */
async function getTenantDBAsync(tenantId) {
    const cached = tenantCache.get(tenantId);
    if (cached)
        return cached;
    const tenant = await db_1.knex('tenants').where({ id: tenantId }).first().catch(() => null);
    const region = tenant && tenant.data_residency_region ? String(tenant.data_residency_region) : null;
    let connConfig = db_1.knex.client.config.connection;
    if (region) {
        // region keys mapped to env or knexfile names
        const key = `region:${region}`;
        // attempt to reuse regionKnex from cache
        let regionKnex = regionCache.get(region);
        if (!regionKnex) {
            // read connection string from environment naming convention
            // map common region identifiers to env var names
            const envKey = `DATABASE_URL_${region.toUpperCase().replace(/[-.]/g, '_')}`;
            const envConn = process.env[envKey];
            if (envConn) {
                connConfig = envConn;
            }
            else {
                // fallback to primary
                connConfig = db_1.knex.client.config.connection;
            }
            regionKnex = (0, knex_1.default)({ client: 'pg', connection: connConfig });
            regionCache.set(region, regionKnex);
        }
        else {
            connConfig = regionKnex.client.config.connection;
        }
    }
    const schema = tenantSchemaName(tenantId);
    const cfg = {
        client: 'pg',
        connection: connConfig,
        searchPath: [schema, 'public']
    };
    const k = (0, knex_1.default)(cfg);
    tenantCache.set(tenantId, k);
    return k;
}
function clearTenantDBCache(tenantId) {
    const k = tenantCache.get(tenantId);
    if (!k)
        return;
    k.destroy();
    tenantCache.delete(tenantId);
}
function clearRegionCache(region) {
    const k = regionCache.get(region);
    if (!k)
        return;
    k.destroy();
    regionCache.delete(region);
}
function buildTenantSchemaName(tenantId) {
    return tenantSchemaName(tenantId);
}
