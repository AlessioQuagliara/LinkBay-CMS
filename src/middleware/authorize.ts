import { RequestHandler } from 'express';

export const authorize = (roles: string[] | string): RequestHandler => {
  const allowed = Array.isArray(roles) ? roles : [roles];
  return (req, res, next) => {
    const user = (req as any).user;
    if (!user) return res.status(401).json({ error: 'not_authenticated' });
    if (!allowed.includes(user.role)) return res.status(403).json({ error: 'forbidden' });
    next();
  };
};
