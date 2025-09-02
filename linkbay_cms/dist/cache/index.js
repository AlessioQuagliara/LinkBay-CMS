"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.cacheGet = cacheGet;
exports.isRedisHealthy = isRedisHealthy;
exports.cacheSet = cacheSet;
exports.cacheDel = cacheDel;
exports.cacheKeyForQuery = cacheKeyForQuery;
exports.cached = cached;
exports.pageCache = pageCache;
const ioredis_1 = __importDefault(require("ioredis"));
const node_cache_1 = __importDefault(require("node-cache"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const redisUrl = process.env.REDIS_URL;
let redis = null;
if (redisUrl) {
    redis = new ioredis_1.default(redisUrl);
}
const localCache = new node_cache_1.default({ stdTTL: 60, checkperiod: 120 });
async function cacheGet(key) {
    if (redis) {
        const v = await redis.get(key);
        return v ? JSON.parse(v) : null;
    }
    const v = localCache.get(key);
    return v || null;
}
async function isRedisHealthy() {
    if (!redis)
        return false;
    try {
        const pong = await redis.ping();
        return pong === 'PONG';
    }
    catch (err) {
        return false;
    }
}
async function cacheSet(key, value, ttlSeconds = 60) {
    if (redis) {
        await redis.set(key, JSON.stringify(value), 'EX', ttlSeconds);
        return;
    }
    localCache.set(key, value, ttlSeconds);
}
async function cacheDel(key) {
    if (redis) {
        await redis.del(key);
        return;
    }
    localCache.del(key);
}
function cacheKeyForQuery(tenantId, sqlIdentifier) {
    return `${tenantId || 'public'}:${sqlIdentifier}`;
}
// helper for caching promise-producing functions
async function cached(key, fn, ttlSeconds = 60) {
    const existing = await cacheGet(key);
    if (existing !== null)
        return existing;
    const val = await fn();
    await cacheSet(key, val, ttlSeconds);
    return val;
}
function pageCache(seconds = 60) {
    return (req, res, next) => {
        res.setHeader('Cache-Control', `public, max-age=${seconds}, s-maxage=${seconds}`);
        next();
    };
}
exports.default = { cacheGet, cacheSet, cacheDel, cached, cacheKeyForQuery, pageCache };
