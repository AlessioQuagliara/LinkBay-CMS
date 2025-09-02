import IORedis from 'ioredis';
import NodeCache from 'node-cache';
import dotenv from 'dotenv';
dotenv.config();

const redisUrl = process.env.REDIS_URL;
let redis: any = null;
if (redisUrl) {
  redis = new IORedis(redisUrl);
}

const localCache = new NodeCache({ stdTTL: 60, checkperiod: 120 });

export async function cacheGet<T>(key: string): Promise<T | null> {
  if (redis) {
    const v = await redis.get(key);
    return v ? JSON.parse(v) : null;
  }
  const v = localCache.get<T>(key);
  return v || null;
}

export async function isRedisHealthy(): Promise<boolean> {
  if (!redis) return false;
  try {
    const pong = await redis.ping();
    return pong === 'PONG';
  } catch (err:any) {
    return false;
  }
}

export async function cacheSet<T>(key: string, value: T, ttlSeconds = 60): Promise<void> {
  if (redis) {
    await redis.set(key, JSON.stringify(value), 'EX', ttlSeconds);
    return;
  }
  localCache.set(key, value, ttlSeconds);
}

export async function cacheDel(key: string): Promise<void> {
  if (redis) {
    await redis.del(key);
    return;
  }
  localCache.del(key);
}

export function cacheKeyForQuery(tenantId: number | null, sqlIdentifier: string) {
  return `${tenantId || 'public'}:${sqlIdentifier}`;
}

// helper for caching promise-producing functions
export async function cached<T>(key: string, fn: ()=>Promise<T>, ttlSeconds = 60): Promise<T> {
  const existing = await cacheGet<T>(key);
  if (existing !== null) return existing;
  const val = await fn();
  await cacheSet(key, val, ttlSeconds);
  return val;
}

// HTTP cache middleware for public pages
import { RequestHandler } from 'express';
export function pageCache(seconds = 60): RequestHandler {
  return (req, res, next) => {
    res.setHeader('Cache-Control', `public, max-age=${seconds}, s-maxage=${seconds}`);
    next();
  };
}

export default { cacheGet, cacheSet, cacheDel, cached, cacheKeyForQuery, pageCache };
