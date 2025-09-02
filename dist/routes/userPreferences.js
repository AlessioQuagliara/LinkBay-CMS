"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const jwtAuth_1 = require("../middleware/jwtAuth");
const router = (0, express_1.Router)();
// GET /api/user/preferences
router.get('/', jwtAuth_1.jwtAuth, async (req, res) => {
    const user = req.user;
    if (!user)
        return res.status(401).json({ error: 'unauthenticated' });
    const rows = await (0, db_1.knex)('user_preferences').where({ user_id: user.id }).select('key', 'value');
    const prefs = {};
    rows.forEach(r => { try {
        prefs[r.key] = JSON.parse(r.value);
    }
    catch (e) {
        prefs[r.key] = r.value;
    } });
    res.json({ preferences: prefs });
});
// PUT /api/user/preferences
// Accepts { preferences: { key: value, ... } }
router.put('/', jwtAuth_1.jwtAuth, async (req, res) => {
    const user = req.user;
    if (!user)
        return res.status(401).json({ error: 'unauthenticated' });
    const prefs = req.body.preferences || {};
    const keys = Object.keys(prefs);
    const trx = await db_1.knex.transaction();
    try {
        for (const k of keys) {
            const raw = typeof prefs[k] === 'string' ? prefs[k] : JSON.stringify(prefs[k]);
            const existing = await trx('user_preferences').where({ user_id: user.id, key: k }).first();
            if (existing) {
                await trx('user_preferences').where({ id: existing.id }).update({ value: raw, updated_at: trx.fn.now() });
            }
            else {
                await trx('user_preferences').insert({ user_id: user.id, key: k, value: raw });
            }
        }
        await trx.commit();
        res.json({ success: true });
    }
    catch (err) {
        await trx.rollback();
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
