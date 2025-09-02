import { RequestHandler } from 'express';
import { verifyToken } from '../services/auth';
import { knex } from '../db';

export const jwtAuth: RequestHandler = async (req, res, next) => {
  const header = (req.headers.authorization as string) || (req.headers['x-access-token'] as string);
  const token = header && header.startsWith('Bearer ') ? header.slice(7) : header;
  if (!token) return res.status(401).json({ error: 'no_token' });
  try {
    const payload: any = verifyToken(token as string);
    const user = await (knex as any)('users').where({ id: payload.id, tenant_id: payload.tenant_id }).first();
    if (!user) return res.status(401).json({ error: 'user_not_found' });
    (req as any).user = user;
    next();
  } catch (err: any) {
    return res.status(401).json({ error: 'invalid_token', message: err && err.message });
  }
};
