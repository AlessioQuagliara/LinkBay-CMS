import { ApolloServer } from 'apollo-server-express';
import { typeDefs } from './schema';
import { resolvers } from './resolvers';
import { knex } from '../db';
import crypto from 'crypto';
import jwt from 'jsonwebtoken';

export async function createGraphQLServer() {
  const server = new ApolloServer({
    typeDefs,
    resolvers,
    context: async ({ req }: any) => {
      // Prefer API key in X-API-Key, else Authorization Bearer JWT
      const apiKeyRaw = req.headers['x-api-key'];
      if (apiKeyRaw) {
        const hash = crypto.createHash('sha256').update(String(apiKeyRaw)).digest('hex');
        const row = await knex('api_keys').where({ key_hash: hash }).first();
        if (!row) throw new Error('invalid_api_key');
        if (row.expires_at && new Date(row.expires_at) < new Date()) throw new Error('api_key_expired');
        return { tenant: { id: row.tenant_id }, apiKey: row };
      }
      const auth = req.headers.authorization || '';
      if (auth.startsWith('Bearer ')){
        const token = auth.slice(7);
        try {
          const payload: any = jwt.verify(token, process.env.SESSION_SECRET || 'secret');
          return { tenant: payload.tenant || null, user: payload.user || null };
        } catch(e){ /* fall through */ }
      }
      return {};
    }
  });
  await server.start();
  return server;
}
