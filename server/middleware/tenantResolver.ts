import { Request, Response, NextFunction } from 'express';

export default async function tenantResolver(req: Request, res: Response, next: NextFunction) {
  // Simple subdomain resolver - adjust to your needs
  const host = req.headers.host || '';
  const subdomain = host.split(':')[0].split('.')[0] || 'default';

  // Attach a minimal tenant object to the request for downstream handlers
  (req as any).tenant = { subdomain };
  next();
}
