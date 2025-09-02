import rateLimit, { RateLimitRequestHandler, ipKeyGenerator } from 'express-rate-limit';
import slowDown from 'express-slow-down';
import { RequestHandler } from 'express';

// Global limiter: moderate limits for all requests (keyed by tenant id when present)
export function globalLimiter() : RequestHandler {
  return rateLimit({
    windowMs: 60 * 1000, // 1 minute
    max: 200, // 200 requests per minute
    keyGenerator: (req:any) => {
      if (req.tenant && req.tenant.id) return `tenant_${req.tenant.id}`;
      // use ipKeyGenerator for IPv6-safe behavior
      return String(req.ip).includes(':') ? ipKeyGenerator(req as any) : String(req.ip);
    },
    standardHeaders: true,
    legacyHeaders: false
  });
}

// Strict limiter for auth endpoints (based on IP)
export function authLimiter() : RateLimitRequestHandler {
  return rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 10, // 10 attempts per 15 minutes per IP
  keyGenerator: (req:any) => String(req.ip).includes(':') ? ipKeyGenerator(req as any) : String(req.ip),
    standardHeaders: true,
    legacyHeaders: false
  });
}

// Exponential backoff middleware for failed login attempts (in-memory simple implementation)
const failedLogins = new Map<string, { attempts: number, lastAt: number }>();
export function loginBackoff(): RequestHandler {
  return async (req:any, res, next) => {
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
    if (rec.attempts > 0) await new Promise(r => setTimeout(r, delay));

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
