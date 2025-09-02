import rateLimit from 'express-rate-limit';
import { RequestHandler } from 'express';
import { getPlanLimits } from '../lib/tenantResourceLimits';

// Cache limiter instances per plan to avoid creating them during request handling
const limiterCache = new Map<string, ReturnType<typeof rateLimit>>();

// Pre-create limiters for known plans to satisfy express-rate-limit requirement
const knownPlans = ['free', 'pro', 'enterprise'];
for (const p of knownPlans) {
  const limits = getPlanLimits(p);
  const l = rateLimit({ windowMs: limits.windowMs, max: limits.maxRequests, keyGenerator: (r:any)=> (r.tenant && r.tenant.id) ? `tenant_${r.tenant.id}` : r.ip });
  limiterCache.set(p, l);
}

export function tenantRateLimiter(): RequestHandler {
  return (req:any, res, next) => {
    const plan = req.tenant && req.tenant.plan_type ? req.tenant.plan_type : 'free';
    let limiter = limiterCache.get(plan);
    if (!limiter) {
      const limits = getPlanLimits(plan);
      limiter = rateLimit({ windowMs: limits.windowMs, max: limits.maxRequests, keyGenerator: (r:any)=> (r.tenant && r.tenant.id) ? `tenant_${r.tenant.id}` : r.ip });
      limiterCache.set(plan, limiter);
    }
    return limiter(req, res, next as any);
  };
}
