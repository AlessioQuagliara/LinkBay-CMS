"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const jwtAuth_1 = require("../middleware/jwtAuth");
const router = (0, express_1.Router)();
// GET status
router.get('/onboarding-status', jwtAuth_1.jwtAuth, async (req, res) => {
    const user = req.user;
    if (!user)
        return res.status(401).json({ error: 'unauthenticated' });
    const row = await (0, db_1.knex)('users').where({ id: user.id }).first();
    res.json({ onboarding_completed: row?.onboarding_completed || false });
});
// POST mark completed
router.post('/onboarding-status', jwtAuth_1.jwtAuth, async (req, res) => {
    const user = req.user;
    if (!user)
        return res.status(401).json({ error: 'unauthenticated' });
    await (0, db_1.knex)('users').where({ id: user.id }).update({ onboarding_completed: true });
    res.json({ onboarding_completed: true });
});
exports.default = router;
