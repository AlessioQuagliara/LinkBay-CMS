import { RequestHandler } from 'express';

const supported = ['en','it','es'];

export const contentLang: RequestHandler = (req, res, next) => {
  // prefer explicit query param
  const q = (req.query.lang || '') as string;
  if (q && supported.includes(q)) { (req as any).contentLang = q; return next(); }
  // detect from URL prefix: /en/slug or /it/...
  const m = req.path.match(/^\/(en|it|es)(?:\/|$)/);
  if (m) { (req as any).contentLang = m[1]; }
  else { (req as any).contentLang = 'en'; }
  next();
};
