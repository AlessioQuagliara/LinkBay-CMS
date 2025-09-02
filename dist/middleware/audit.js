"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.logAuditEvent = logAuditEvent;
exports.writeAudit = writeAudit;
exports.auditChange = auditChange;
const db_1 = require("../db");
function logAuditEvent(action, extractMetadata) {
    return async (req, res, next) => {
        try {
            const tenant = req.tenant || null;
            const user = req.user || null;
            const metadata = extractMetadata ? await extractMetadata(req, res) : {};
            await db_1.knex('audit_logs').insert({
                tenant_id: tenant ? tenant.id : null,
                user_id: user ? user.id : null,
                action,
                ip_address: req.ip || req.headers['x-forwarded-for'] || null,
                user_agent: (req.headers && req.headers['user-agent']) || null,
                metadata: JSON.stringify(metadata || {})
            });
        }
        catch (err) {
            // don't block the request on audit failures
            console.error('audit log failed', err && err.message);
        }
        next();
    };
}
// helper to log ad-hoc events from code
async function writeAudit(action, ctx) {
    try {
        await db_1.knex('audit_logs').insert({
            tenant_id: ctx.tenantId || null,
            user_id: ctx.userId || null,
            action,
            ip_address: ctx.ip || null,
            user_agent: ctx.ua || null,
            metadata: JSON.stringify(ctx.metadata || {})
        });
    }
    catch (err) {
        console.error('writeAudit failed', err && err.message);
    }
}
// auditChange records old and new values in metadata for update events
async function auditChange(action, ctx) {
    try {
        const payload = Object.assign({}, ctx.metadata || {}, { old_value: ctx.oldValue || null, new_value: ctx.newValue || null });
        await db_1.knex('audit_logs').insert({
            tenant_id: ctx.tenantId || null,
            user_id: ctx.userId || null,
            action,
            ip_address: ctx.ip || null,
            user_agent: ctx.ua || null,
            metadata: JSON.stringify(payload || {})
        });
    }
    catch (err) {
        console.error('auditChange failed', err && err.message);
    }
}
