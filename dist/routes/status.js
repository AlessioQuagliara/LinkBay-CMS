"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const simpleCache_1 = __importDefault(require("../lib/simpleCache"));
const db_1 = require("../db");
const analyticsConsumer_1 = require("../lib/analyticsConsumer");
const cache_1 = require("../cache");
const router = express_1.default.Router();
// JSON status with caching
router.get('/status.json', async (req, res) => {
    const cached = simpleCache_1.default.get('platform_status');
    if (cached)
        return res.json(cached);
    const status = { ok: true, checks: {}, timestamp: new Date().toISOString() };
    try {
        await db_1.knex.raw('select 1');
        status.checks.database = { ok: true };
    }
    catch (err) {
        status.ok = false;
        status.checks.database = { ok: false, error: String(err) };
    }
    try {
        // analyticsKnex may be a function or object depending on import
        if (analyticsConsumer_1.analyticsKnex && typeof analyticsConsumer_1.analyticsKnex.raw === 'function') {
            await analyticsConsumer_1.analyticsKnex.raw('select 1');
            status.checks.analytics_db = { ok: true };
        }
    }
    catch (err) {
        status.ok = false;
        status.checks.analytics_db = { ok: false, error: String(err) };
    }
    try {
        const redisOk = await (0, cache_1.isRedisHealthy)();
        status.checks.redis = { ok: !!redisOk };
        if (!redisOk)
            status.ok = false;
    }
    catch (err) {
        status.ok = false;
        status.checks.redis = { ok: false, error: String(err) };
    }
    // incidents placeholder: try to read from a table `status_incidents` if exists
    try {
        const exists = await db_1.knex.schema.hasTable('status_incidents');
        if (exists) {
            const incidents = await (0, db_1.knex)('status_incidents').select('id', 'severity', 'title', 'body', 'created_at').where('active', true).orderBy('created_at', 'desc');
            status.incidents = incidents;
        }
        else {
            status.incidents = [];
        }
    }
    catch (err) {
        // non-fatal
        status.incidents = [];
    }
    simpleCache_1.default.set('platform_status', status, 20); // short TTL
    res.json(status);
});
// Public status page
router.get('/status', async (req, res) => {
    const cached = simpleCache_1.default.get('platform_status_html');
    if (cached)
        return res.send(cached);
    // reuse the json route logic
    const resp = await (async () => {
        const r = await fetch((req.protocol || 'http') + '://' + req.get('host') + '/status.json');
        return r.json();
    })();
    const html = await new Promise((resolve, reject) => {
        res.render('status', { status: resp }, (err, str) => {
            if (err)
                return reject(err);
            resolve(str || '');
        });
    });
    simpleCache_1.default.set('platform_status_html', html, 20);
    res.send(html);
});
exports.default = router;
