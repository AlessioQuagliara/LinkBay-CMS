import { RequestHandler } from 'express';
import { knex } from '../db';

export type MetadataExtractor = (req: any, res: any) => Promise<any> | any;

export function logAuditEvent(action: string, extractMetadata?: MetadataExtractor): RequestHandler {
  return async (req: any, res, next) => {
    try {
      const tenant = req.tenant || null;
      const user = req.user || null;
      const metadata = extractMetadata ? await extractMetadata(req, res) : {};
      await (knex as any)('audit_logs').insert({
        tenant_id: tenant ? tenant.id : null,
        user_id: user ? user.id : null,
        action,
        ip_address: req.ip || req.headers['x-forwarded-for'] || null,
        user_agent: (req.headers && req.headers['user-agent']) || null,
        metadata: JSON.stringify(metadata || {})
      });
    } catch (err:any) {
      // don't block the request on audit failures
      console.error('audit log failed', err && err.message);
    }
    next();
  };
}

// helper to log ad-hoc events from code
export async function writeAudit(action: string, ctx: { tenantId?: number, userId?: number, ip?: string, ua?: string, metadata?: any }) {
  try {
    await (knex as any)('audit_logs').insert({
      tenant_id: ctx.tenantId || null,
      user_id: ctx.userId || null,
      action,
      ip_address: ctx.ip || null,
      user_agent: ctx.ua || null,
      metadata: JSON.stringify(ctx.metadata || {})
    });
  } catch (err:any) {
    console.error('writeAudit failed', err && err.message);
  }
}

// auditChange records old and new values in metadata for update events
export async function auditChange(action: string, ctx: { tenantId?: number, userId?: number, ip?: string, ua?: string, oldValue?: any, newValue?: any, metadata?: any }) {
  try {
    const payload = Object.assign({}, ctx.metadata || {}, { old_value: ctx.oldValue || null, new_value: ctx.newValue || null });
    await (knex as any)('audit_logs').insert({
      tenant_id: ctx.tenantId || null,
      user_id: ctx.userId || null,
      action,
      ip_address: ctx.ip || null,
      user_agent: ctx.ua || null,
      metadata: JSON.stringify(payload || {})
    });
  } catch (err:any) {
    console.error('auditChange failed', err && err.message);
  }
}
