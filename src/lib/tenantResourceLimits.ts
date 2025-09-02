type PlanLimits = { maxRequests:number; windowMs:number; queryTimeoutMs:number; apiTimeoutMs:number; workerTaskTimeoutMs:number };

const PLANS: Record<string, PlanLimits> = {
  free: { maxRequests: 60, windowMs: 60*1000, queryTimeoutMs: 2000, apiTimeoutMs: 5000, workerTaskTimeoutMs: 5000 },
  pro:  { maxRequests: 600, windowMs: 60*1000, queryTimeoutMs: 10000, apiTimeoutMs: 20000, workerTaskTimeoutMs: 20000 },
  enterprise: { maxRequests: 5000, windowMs: 60*1000, queryTimeoutMs: 60000, apiTimeoutMs: 120000, workerTaskTimeoutMs: 120000 }
};

export function getPlanLimits(planType: string): PlanLimits {
  return PLANS[planType] || PLANS['free'];
}

// Helper to apply query timeout on knex query builder
export function applyQueryTimeout<T extends { timeout?: (ms:number)=>any }>(qb: T, planType: string) {
  const limits = getPlanLimits(planType);
  if (typeof qb.timeout === 'function') qb.timeout(limits.queryTimeoutMs);
  return qb;
}

export default { getPlanLimits, applyQueryTimeout };
