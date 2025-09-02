"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.createTenantSchema = createTenantSchema;
const db_1 = require("../db");
const dbMultiTenant_1 = require("../dbMultiTenant");
async function createTenantSchema(tenantId) {
    const schema = (0, dbMultiTenant_1.buildTenantSchemaName)(tenantId);
    // create schema and run tenant migrations via DB helper function
    await db_1.knex.raw(`CREATE SCHEMA IF NOT EXISTS "${schema}"`);
    await db_1.knex.raw(`SELECT create_tenant_schema('${schema}')`);
    await db_1.knex.raw(`SELECT create_tenant_ecommerce_schema('${schema}')`);
}
