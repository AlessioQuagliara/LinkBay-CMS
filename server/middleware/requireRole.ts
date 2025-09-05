import { Request, Response, NextFunction } from 'express';
import { initDb } from '../../src/db';

type Role = 'owner' | 'admin' | 'member';

interface ReqWithUser extends Request {
  user?: any;
  tenant?: any;
}

export default function requireRole(allowed: Role | Role[]) {
  const allowedArr = Array.isArray(allowed) ? allowed : [allowed];
  return async (req: ReqWithUser, res: Response, next: NextFunction) => {
    try {
      const user = req.user;
      const tenant = req.tenant;
      if (!user || !tenant) return res.status(401).json({ ok: false, error: 'Not authenticated or tenant missing' });

      // load user record from db to ensure role and tenant
      const db = await initDb();
      const dbUser = await db('users').where({ id: user.id, tenant_id: tenant.id }).first();
      if (!dbUser) return res.status(403).json({ ok: false, error: 'User not part of tenant' });

      if (!allowedArr.includes(dbUser.role as Role)) return res.status(403).json({ ok: false, error: 'Insufficient role' });

      // attach fresh user
      req.user = dbUser;
      return next();
    } catch (err: any) {
      // eslint-disable-next-line no-console
      console.error('requireRole error:', err);
      return res.status(500).json({ ok: false, error: 'Internal error' });
    }
  };
}
