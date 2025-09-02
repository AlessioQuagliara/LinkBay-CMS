"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.requireApiKey = requireApiKey;
exports.requireScope = requireScope;
const crypto_1 = __importDefault(require("crypto"));
const db_1 = require("../db");
// Simple API key verifier: expects X-API-Key header with raw key
async function requireApiKey(req, res, next) {
    const raw = req.headers['x-api-key'] || '';
    if (!raw)
        return res.status(401).json({ error: 'api_key_required' });
    try {
        const hash = crypto_1.default.createHash('sha256').update(raw).digest('hex');
        const row = await (0, db_1.knex)('api_keys').where({ key_hash: hash }).first();
        if (!row)
            return res.status(401).json({ error: 'invalid_api_key' });
        if (row.expires_at && new Date(row.expires_at) < new Date())
            return res.status(401).json({ error: 'api_key_expired' });
        // attach tenant info and scopes
        req.tenant = { id: row.tenant_id };
        let scopes = null;
        try {
            scopes = row.scopes ? (Array.isArray(row.scopes) ? row.scopes : JSON.parse(row.scopes)) : [];
        }
        catch (e) {
            scopes = row.scopes || [];
        }
        req.apiKey = { id: row.id, scopes };
        return next();
    }
    catch (err) {
        console.error('api key check error', err);
        return res.status(500).json({ error: 'server_error' });
    }
}
// Middleware factory to require a specific scope
function requireScope(scope) {
    return (req, res, next) => {
        const apiKey = req.apiKey;
        if (!apiKey)
            return res.status(403).json({ error: 'no_api_key' });
        if (!Array.isArray(apiKey.scopes))
            return res.status(403).json({ error: 'invalid_scopes' });
        if (apiKey.scopes.includes(scope) || apiKey.scopes.includes('*'))
            return next();
        return res.status(403).json({ error: 'insufficient_scope' });
    };
}
