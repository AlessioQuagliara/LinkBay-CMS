"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createGraphQLServer = createGraphQLServer;
const apollo_server_express_1 = require("apollo-server-express");
const schema_1 = require("./schema");
const resolvers_1 = require("./resolvers");
const db_1 = require("../db");
const crypto_1 = __importDefault(require("crypto"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
async function createGraphQLServer() {
    const server = new apollo_server_express_1.ApolloServer({
        typeDefs: schema_1.typeDefs,
        resolvers: resolvers_1.resolvers,
        context: async ({ req }) => {
            // Prefer API key in X-API-Key, else Authorization Bearer JWT
            const apiKeyRaw = req.headers['x-api-key'];
            if (apiKeyRaw) {
                const hash = crypto_1.default.createHash('sha256').update(String(apiKeyRaw)).digest('hex');
                const row = await (0, db_1.knex)('api_keys').where({ key_hash: hash }).first();
                if (!row)
                    throw new Error('invalid_api_key');
                if (row.expires_at && new Date(row.expires_at) < new Date())
                    throw new Error('api_key_expired');
                return { tenant: { id: row.tenant_id }, apiKey: row };
            }
            const auth = req.headers.authorization || '';
            if (auth.startsWith('Bearer ')) {
                const token = auth.slice(7);
                try {
                    const payload = jsonwebtoken_1.default.verify(token, process.env.SESSION_SECRET || 'secret');
                    return { tenant: payload.tenant || null, user: payload.user || null };
                }
                catch (e) { /* fall through */ }
            }
            return {};
        }
    });
    await server.start();
    return server;
}
