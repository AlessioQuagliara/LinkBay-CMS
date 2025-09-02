import { RequestHandler } from 'express';
import { getPlanLimits } from '../lib/tenantResourceLimits';

export function tenantApiTimeout(): RequestHandler {
  return (req:any, res, next) => {
    const plan = req.tenant && req.tenant.plan_type ? req.tenant.plan_type : 'free';
    const limits = getPlanLimits(plan);
    // set socket timeout for the response
    res.setTimeout(limits.apiTimeoutMs, () => {
      try { res.status(504).json({ error: 'request_timeout' }); } catch(e){}
    });
    next();
  };
}
