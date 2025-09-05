import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { initDb } from '../../src/db';

interface ReqWithTenant extends Request {
  tenant?: any;
}

export default async function authenticateTenant(req: ReqWithTenant, res: Response, next: NextFunction) {
  try {
    const sessionTenant = (req.session as any)?.tenantName;

    let tenantName: string | undefined = sessionTenant;

    // If no session, check Authorization Bearer JWT
    if (!tenantName && req.headers.authorization?.startsWith('Bearer ')) {
      const token = req.headers.authorization.slice(7);
      const secret = process.env.JWT_SECRET;
      if (!secret) return res.status(500).json({ ok: false, error: 'JWT secret not configured' });
      try {
        const payload: any = jwt.verify(token, secret);
        tenantName = payload?.tenantName;
      } catch (err) {
        return res.status(401).json({ ok: false, error: 'Invalid token' });
      }
    }

    if (!tenantName) return res.status(401).json({ ok: false, error: 'Tenant not specified' });

    const db = await initDb();
    const tenant = await db('tenants').where({ name: tenantName }).first();
    if (!tenant) return res.status(404).json({ ok: false, error: 'Tenant not found' });

    req.tenant = tenant;
    return next();
  } catch (err: any) {
    // eslint-disable-next-line no-console
    console.error('authenticateTenant error:', err);
    return res.status(500).json({ ok: false, error: 'Internal error' });
  }
}
