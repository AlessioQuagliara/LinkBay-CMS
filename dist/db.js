"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.knex = void 0;
const knex_1 = __importDefault(require("knex"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
exports.knex = (0, knex_1.default)({ client: 'pg', connection: process.env.DATABASE_URL });
// Instrument queries to log slow queries in development
if (process.env.NODE_ENV !== 'production') {
    exports.knex.on('query', (query) => {
        query._start = Date.now();
    });
    exports.knex.on('query-response', async (response, query) => {
        try {
            const duration = Date.now() - query._start;
            if (duration > 100) {
                const text = (query && query.sql) ? query.sql : JSON.stringify(query);
                console.warn(`SLOW QUERY ${duration}ms: ${text}`);
                // insert into audit_logs for later inspection if table exists
                try {
                    await exports.knex('audit_logs').insert({ action: 'db.slow_query', metadata: JSON.stringify({ sql: text, duration }), created_at: new Date() });
                }
                catch (err) {
                    // ignore
                }
            }
        }
        catch (err) {
            // ignore
        }
    });
}
