"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const dbMultiTenant_1 = require("../dbMultiTenant");
const router = (0, express_1.Router)();
function mapColumnsToCategory(cols) {
    // very small heuristic mapping based on column names
    const categories = new Set();
    Object.keys(cols).forEach(c => {
        const name = c.toLowerCase();
        if (name.includes('email') || name.includes('phone') || name.includes('address'))
            categories.add('Contact information');
        if (name.includes('name') || name.includes('first_name') || name.includes('last_name'))
            categories.add('Identifiers');
        if (name.includes('password') || name.includes('hash'))
            categories.add('Credentials');
        if (name.includes('card') || name.includes('payment') || name.includes('billing'))
            categories.add('Financial / Payment data');
        if (name.includes('ssn') || name.includes('tax'))
            categories.add('Sensitive identifiers');
        if (name.includes('ip') || name.includes('user_agent') || name.includes('activity') || name.includes('analytics'))
            categories.add('Behavioral / Analytics');
        if (name.includes('notes') || name.includes('message') || name.includes('conversation') || name.includes('support'))
            categories.add('Support / Communications');
    });
    return Array.from(categories);
}
// GET /api/tenant/data-processing-activities
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    try {
        const tenantDb = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
        const result = {};
        // 1) categories of personal data collected: inspect common tables' columns
        const tablesToInspect = ['users', 'orders', 'conversations', 'user_activity_logs', 'audit_logs', 'payments', 'api_keys'];
        const collected = {};
        for (const table of tablesToInspect) {
            try {
                const info = await tenantDb(table).columnInfo();
                const cols = Object.keys(info || {});
                if (cols.length) {
                    collected[table] = { columns: cols, categories: mapColumnsToCategory(info) };
                }
            }
            catch (e) {
                // table not present in tenant schema
            }
        }
        result.categories_of_data_collected = collected;
        // 2) purposes of processing: infer from active features
        const purposes = [];
        // tracking scripts
        const tenantSettings = req.tenantSettings || await (0, db_1.knex)('tenant_settings').where({ tenant_id: tenant.id }).first().catch(() => null);
        if (tenantSettings && tenantSettings.tracking_scripts) {
            purposes.push({ feature: 'Tracking scripts', description: 'Third-party tracking and analytics scripts configured in tenant settings', evidence: { tracking_scripts: true } });
        }
        // active tenant plugins
        const activePlugins = await (0, db_1.knex)('tenant_plugins').where({ tenant_id: tenant.id, is_active: true }).select('plugin_id', 'config').catch(() => []);
        if (activePlugins && activePlugins.length) {
            purposes.push({ feature: 'Plugins', description: 'Installed tenant plugins that may process customer data', evidence: activePlugins.map((p) => ({ plugin_id: p.plugin_id, config: p.config })) });
        }
        // active integrations (third-party integrations)
        const integrations = await (0, db_1.knex)('tenant_integrations').where({ tenant_id: tenant.id, is_active: true }).select('provider', 'config').catch(() => []);
        if (integrations && integrations.length) {
            purposes.push({ feature: 'Integrations', description: 'Connected integrations which may transfer data to third-parties', evidence: integrations.map((i) => ({ provider: i.provider, config: i.config })) });
        }
        result.purposes = purposes;
        // 3) Transfers to third parties: map integrations to subprocessors if possible
        const transfers = [];
        for (const integ of (integrations || [])) {
            const provider = String(integ.provider || '').toLowerCase();
            let subprocessors = [];
            try {
                // try exact match or LIKE
                subprocessors = await (0, db_1.knex)('subprocessors').whereRaw('LOWER(name) = ?', [provider]).orWhere('name', 'ilike', `%${provider}%`).select('name', 'purpose', 'data_centers');
            }
            catch (e) {
                subprocessors = [];
            }
            transfers.push({ integration: provider, subprocessors });
        }
        result.third_party_transfers = transfers;
        // 4) retention periods: read retention_policies per-tenant or global
        const keys = ['audit_logs_retention_days', 'user_activity_logs_retention_days', 'orders_retention_days'];
        const retention = {};
        for (const k of keys) {
            let row = await (0, db_1.knex)('retention_policies').where({ tenant_id: tenant.id, key: k }).first().catch(() => null);
            if (!row)
                row = await (0, db_1.knex)('retention_policies').where({ tenant_id: null, key: k }).first().catch(() => null);
            retention[k] = row ? Number(row.value_days) : null;
        }
        result.retention_periods = retention;
        // additional helper metadata
        result.meta = { tenant_id: tenant.id, schema: (0, dbMultiTenant_1.buildTenantSchemaName)(tenant.id), generated_at: new Date().toISOString() };
        res.json({ success: true, report: result });
    }
    catch (err) {
        console.error('dpia generation failed', err && err.message);
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
