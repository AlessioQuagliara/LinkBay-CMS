import cors from 'cors';
import { RequestHandler } from 'express';

const whitelist = [ 'https://linkbay.example.com' ];

export const dynamicCors: RequestHandler = (req, res, next) => {
  const origin = req.headers.origin as string | undefined;
  // tenant domains would be looked up from tenant config; allow if in whitelist for now
  if (!origin) return next();
  if (whitelist.includes(origin)) return cors({ origin })(req as any, res as any, next as any);
  return next();
};
