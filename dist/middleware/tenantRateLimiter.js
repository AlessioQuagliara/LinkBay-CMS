"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.tenantRateLimiter = tenantRateLimiter;
const express_rate_limit_1 = __importDefault(require("express-rate-limit"));
const tenantResourceLimits_1 = require("../lib/tenantResourceLimits");
// Cache limiter instances per plan to avoid creating them during request handling
const limiterCache = new Map();
// Pre-create limiters for known plans to satisfy express-rate-limit requirement
const knownPlans = ['free', 'pro', 'enterprise'];
for (const p of knownPlans) {
    const limits = (0, tenantResourceLimits_1.getPlanLimits)(p);
    const l = (0, express_rate_limit_1.default)({ windowMs: limits.windowMs, max: limits.maxRequests, keyGenerator: (r) => (r.tenant && r.tenant.id) ? `tenant_${r.tenant.id}` : r.ip });
    limiterCache.set(p, l);
}
function tenantRateLimiter() {
    return (req, res, next) => {
        const plan = req.tenant && req.tenant.plan_type ? req.tenant.plan_type : 'free';
        let limiter = limiterCache.get(plan);
        if (!limiter) {
            const limits = (0, tenantResourceLimits_1.getPlanLimits)(plan);
            limiter = (0, express_rate_limit_1.default)({ windowMs: limits.windowMs, max: limits.maxRequests, keyGenerator: (r) => (r.tenant && r.tenant.id) ? `tenant_${r.tenant.id}` : r.ip });
            limiterCache.set(plan, limiter);
        }
        return limiter(req, res, next);
    };
}
