import express from 'express';
import cache from '../lib/simpleCache';
import { knex } from '../db';
import { analyticsKnex } from '../lib/analyticsConsumer';
import { isRedisHealthy } from '../cache';

const router = express.Router();

// JSON status with caching
router.get('/status.json', async (req, res) => {
  const cached = cache.get('platform_status');
  if (cached) return res.json(cached);

  const status: any = { ok: true, checks: {}, timestamp: new Date().toISOString() };

  try {
    await knex.raw('select 1');
    status.checks.database = { ok: true };
  } catch (err) {
    status.ok = false;
    status.checks.database = { ok: false, error: String(err) };
  }

  try {
    // analyticsKnex may be a function or object depending on import
    if (analyticsKnex && typeof (analyticsKnex as any).raw === 'function') {
      await (analyticsKnex as any).raw('select 1');
      status.checks.analytics_db = { ok: true };
    }
  } catch (err) {
    status.ok = false;
    status.checks.analytics_db = { ok: false, error: String(err) };
  }

  try {
    const redisOk = await isRedisHealthy();
    status.checks.redis = { ok: !!redisOk };
    if (!redisOk) status.ok = false;
  } catch (err) {
    status.ok = false;
    status.checks.redis = { ok: false, error: String(err) };
  }

  // incidents placeholder: try to read from a table `status_incidents` if exists
  try {
    const exists = await knex.schema.hasTable('status_incidents');
    if (exists) {
      const incidents = await knex('status_incidents').select('id', 'severity', 'title', 'body', 'created_at').where('active', true).orderBy('created_at', 'desc');
      status.incidents = incidents;
    } else {
      status.incidents = [];
    }
  } catch (err) {
    // non-fatal
    status.incidents = [];
  }

  cache.set('platform_status', status, 20); // short TTL
  res.json(status);
});

// Public status page
router.get('/status', async (req, res) => {
  const cached = cache.get('platform_status_html');
  if (cached) return res.send(cached);

  // reuse the json route logic
  const resp = await (async () => {
    const r = await fetch((req.protocol || 'http') + '://' + req.get('host') + '/status.json');
    return r.json();
  })();

  const html = await new Promise<string>((resolve, reject) => {
    res.render('status', { status: resp }, (err, str) => {
      if (err) return reject(err);
      resolve(str || '');
    });
  });

  cache.set('platform_status_html', html, 20);
  res.send(html);
});

export default router;
