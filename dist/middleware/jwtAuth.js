"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.jwtAuth = void 0;
const auth_1 = require("../services/auth");
const db_1 = require("../db");
const jwtAuth = async (req, res, next) => {
    const header = req.headers.authorization || req.headers['x-access-token'];
    const token = header && header.startsWith('Bearer ') ? header.slice(7) : header;
    if (!token)
        return res.status(401).json({ error: 'no_token' });
    try {
        const payload = (0, auth_1.verifyToken)(token);
        const user = await db_1.knex('users').where({ id: payload.id, tenant_id: payload.tenant_id }).first();
        if (!user)
            return res.status(401).json({ error: 'user_not_found' });
        req.user = user;
        next();
    }
    catch (err) {
        return res.status(401).json({ error: 'invalid_token', message: err && err.message });
    }
};
exports.jwtAuth = jwtAuth;
