"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = partialCacheMiddleware;
// Simple in-memory cache for rendered partials.
// Stores rendered HTML in app.locals to avoid repeated file IO/rendering on every request.
function partialCacheMiddleware(req, res, next) {
    const app = req.app;
    // ensure container exists
    app.locals.partialCache = app.locals.partialCache || {};
    // if footer cached, attach to res.locals for templates; otherwise render and cache lazily
    if (app.locals.partialCache.footer) {
        res.locals.footer_cached = app.locals.partialCache.footer;
        return next();
    }
    // render footer partial once and cache it
    try {
        app.render('partials/footer', {}, (err, html) => {
            if (!err) {
                app.locals.partialCache.footer = html;
                res.locals.footer_cached = html;
            }
            // ignore render errors and continue without cached footer
            return next();
        });
    }
    catch (e) {
        return next();
    }
}
