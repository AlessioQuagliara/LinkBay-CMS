import { Request, Response, NextFunction } from 'express';

// Simple in-memory cache for rendered partials.
// Stores rendered HTML in app.locals to avoid repeated file IO/rendering on every request.
export default function partialCacheMiddleware(req: Request, res: Response, next: NextFunction) {
  const app = req.app as any;
  // ensure container exists
  app.locals.partialCache = app.locals.partialCache || {};

  // if footer cached, attach to res.locals for templates; otherwise render and cache lazily
  if (app.locals.partialCache.footer) {
    res.locals.footer_cached = app.locals.partialCache.footer;
    return next();
  }

  // render footer partial once and cache it
  try {
    app.render('partials/footer', {}, (err: any, html: string) => {
      if (!err) {
        app.locals.partialCache.footer = html;
        res.locals.footer_cached = html;
      }
      // ignore render errors and continue without cached footer
      return next();
    });
  } catch (e) {
    return next();
  }
}
