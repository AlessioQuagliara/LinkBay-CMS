import { Router } from 'express';
import cache from '../cache';
import { knex } from '../db';

const router = Router();

// Public API: list active subprocessors (heavily cacheable)
router.get('/', async (req, res) => {
  try {
    const key = 'public:subprocessors:active';
    const rows = await cache.cached(key, async () => {
      const r = await (knex as any)('subprocessors').where({ is_active: true }).select('id','name','purpose','data_centers','notes','created_at');
      return r;
    }, 60 * 60 * 24); // cache 24h
    res.json({ success: true, subprocessors: rows });
  } catch (err:any) {
    res.status(500).json({ error: 'server_error' });
  }
});

export default router;
