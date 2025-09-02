import { Router } from 'express';
import { knex } from '../db';
import os from 'os';
import fs from 'fs';
import { execSync } from 'child_process';
import { isRedisHealthy } from '../cache';

const router = Router();

router.get('/', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

router.get('/advanced', async (req, res) => {
  // DB check
  try {
    await knex.raw('select 1');
  } catch (err:any) {
    return res.status(500).json({ error: 'db_unavailable' });
  }

  // Redis check (if configured)
  if (process.env.REDIS_URL) {
    const ok = await isRedisHealthy();
    if (!ok) return res.status(500).json({ error: 'redis_unavailable' });
  }

  // Disk space check on current working dir (use df -k)
  try {
    const cwd = process.cwd();
    const out = execSync(`df -k ${cwd}`).toString();
    // parse last line
    const lines = out.trim().split('\n');
    const last = lines[lines.length-1].split(/\s+/);
    const availKb = Number(last[3] || last[last.length-3]);
    if (isNaN(availKb) || availKb < 1024 * 100) return res.status(500).json({ error: 'low_disk' });
  } catch (err:any) {
    return res.status(500).json({ error: 'disk_check_failed' });
  }

  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

export default router;

