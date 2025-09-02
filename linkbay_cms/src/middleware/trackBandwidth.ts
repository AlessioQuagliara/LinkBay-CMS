import { RequestHandler } from 'express';
import { knex } from '../db';

export const trackBandwidth: RequestHandler = (req:any, res:any, next) => {
  const tenantId = req.tenant && req.tenant.id ? req.tenant.id : req.headers['x-tenant-id'];
  if (!tenantId) return next();
  let bytes = 0;
  const origWrite = res.write;
  const origEnd = res.end;

  (res as any).write = function (chunk: any, encoding: any, cb: any) {
    try { if (chunk) bytes += Buffer.byteLength(typeof chunk === 'string' ? chunk : chunk instanceof Buffer ? chunk : JSON.stringify(chunk)); } catch(e){}
    return origWrite.apply(res, arguments as any);
  };
  (res as any).end = function (chunk:any, encoding:any, cb:any) {
    try { if (chunk) bytes += Buffer.byteLength(typeof chunk === 'string' ? chunk : chunk instanceof Buffer ? chunk : JSON.stringify(chunk)); } catch(e){}
    try { if (bytes > 0) knex('tenants').where({ id: tenantId }).increment('monthly_bandwidth_bytes', Number(bytes)); } catch(e){}
    return origEnd.apply(res, arguments as any);
  };
  next();
};
