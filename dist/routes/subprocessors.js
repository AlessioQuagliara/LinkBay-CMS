"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const cache_1 = __importDefault(require("../cache"));
const db_1 = require("../db");
const router = (0, express_1.Router)();
// Public API: list active subprocessors (heavily cacheable)
router.get('/', async (req, res) => {
    try {
        const key = 'public:subprocessors:active';
        const rows = await cache_1.default.cached(key, async () => {
            const r = await db_1.knex('subprocessors').where({ is_active: true }).select('id', 'name', 'purpose', 'data_centers', 'notes', 'created_at');
            return r;
        }, 60 * 60 * 24); // cache 24h
        res.json({ success: true, subprocessors: rows });
    }
    catch (err) {
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
