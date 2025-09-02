"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.globalLimiter = globalLimiter;
exports.authLimiter = authLimiter;
exports.loginBackoff = loginBackoff;
const express_rate_limit_1 = __importStar(require("express-rate-limit"));
// Global limiter: moderate limits for all requests (keyed by tenant id when present)
function globalLimiter() {
    return (0, express_rate_limit_1.default)({
        windowMs: 60 * 1000, // 1 minute
        max: 200, // 200 requests per minute
        keyGenerator: (req) => {
            if (req.tenant && req.tenant.id)
                return `tenant_${req.tenant.id}`;
            // use ipKeyGenerator for IPv6-safe behavior
            return String(req.ip).includes(':') ? (0, express_rate_limit_1.ipKeyGenerator)(req) : String(req.ip);
        },
        standardHeaders: true,
        legacyHeaders: false
    });
}
// Strict limiter for auth endpoints (based on IP)
function authLimiter() {
    return (0, express_rate_limit_1.default)({
        windowMs: 15 * 60 * 1000, // 15 minutes
        max: 10, // 10 attempts per 15 minutes per IP
        keyGenerator: (req) => String(req.ip).includes(':') ? (0, express_rate_limit_1.ipKeyGenerator)(req) : String(req.ip),
        standardHeaders: true,
        legacyHeaders: false
    });
}
// Exponential backoff middleware for failed login attempts (in-memory simple implementation)
const failedLogins = new Map();
function loginBackoff() {
    return async (req, res, next) => {
        const ip = req.ip;
        const rec = failedLogins.get(ip) || { attempts: 0, lastAt: 0 };
        const now = Date.now();
        // decay attempts every 30 minutes
        if (now - rec.lastAt > 30 * 60 * 1000) {
            rec.attempts = Math.max(0, rec.attempts - 1);
        }
        rec.lastAt = now;
        failedLogins.set(ip, rec);
        // compute delay in ms: base 500ms * 2^attempts, cap 8s
        const delay = Math.min(8000, 500 * Math.pow(2, rec.attempts));
        if (rec.attempts > 0)
            await new Promise(r => setTimeout(r, delay));
        // attach helper to increment attempts when login fails
        req.incrementFailedLogin = () => {
            const r = failedLogins.get(ip) || { attempts: 0, lastAt: Date.now() };
            r.attempts = Math.min(10, r.attempts + 1);
            r.lastAt = Date.now();
            failedLogins.set(ip, r);
        };
        next();
    };
}
