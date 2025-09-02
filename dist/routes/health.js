"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const child_process_1 = require("child_process");
const cache_1 = require("../cache");
const router = (0, express_1.Router)();
router.get('/', (req, res) => {
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});
router.get('/advanced', async (req, res) => {
    // DB check
    try {
        await db_1.knex.raw('select 1');
    }
    catch (err) {
        return res.status(500).json({ error: 'db_unavailable' });
    }
    // Redis check (if configured)
    if (process.env.REDIS_URL) {
        const ok = await (0, cache_1.isRedisHealthy)();
        if (!ok)
            return res.status(500).json({ error: 'redis_unavailable' });
    }
    // Disk space check on current working dir (use df -k)
    try {
        const cwd = process.cwd();
        const out = (0, child_process_1.execSync)(`df -k ${cwd}`).toString();
        // parse last line
        const lines = out.trim().split('\n');
        const last = lines[lines.length - 1].split(/\s+/);
        const availKb = Number(last[3] || last[last.length - 3]);
        if (isNaN(availKb) || availKb < 1024 * 100)
            return res.status(500).json({ error: 'low_disk' });
    }
    catch (err) {
        return res.status(500).json({ error: 'disk_check_failed' });
    }
    res.json({ status: 'OK', timestamp: new Date().toISOString() });
});
exports.default = router;
