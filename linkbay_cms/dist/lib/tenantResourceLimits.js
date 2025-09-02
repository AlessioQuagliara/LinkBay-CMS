"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPlanLimits = getPlanLimits;
exports.applyQueryTimeout = applyQueryTimeout;
const PLANS = {
    free: { maxRequests: 60, windowMs: 60 * 1000, queryTimeoutMs: 2000, apiTimeoutMs: 5000, workerTaskTimeoutMs: 5000 },
    pro: { maxRequests: 600, windowMs: 60 * 1000, queryTimeoutMs: 10000, apiTimeoutMs: 20000, workerTaskTimeoutMs: 20000 },
    enterprise: { maxRequests: 5000, windowMs: 60 * 1000, queryTimeoutMs: 60000, apiTimeoutMs: 120000, workerTaskTimeoutMs: 120000 }
};
function getPlanLimits(planType) {
    return PLANS[planType] || PLANS['free'];
}
// Helper to apply query timeout on knex query builder
function applyQueryTimeout(qb, planType) {
    const limits = getPlanLimits(planType);
    if (typeof qb.timeout === 'function')
        qb.timeout(limits.queryTimeoutMs);
    return qb;
}
exports.default = { getPlanLimits, applyQueryTimeout };
