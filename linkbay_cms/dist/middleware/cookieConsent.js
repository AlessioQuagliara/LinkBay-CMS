"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.cookieConsentMiddleware = void 0;
// This middleware injects a helper in res.locals so templates can render scripts with data-cookie-category and they
// will not be immediately included unless consent cookie allows it. It doesn't mutate response body here, templates
// should use data-src instead of src to defer loading.
const cookieConsentMiddleware = (req, res, next) => {
    // helper to check consent from cookie
    res.locals.cookieConsent = function () {
        try {
            const c = (req.headers.cookie || '').split(';').map((s) => s.trim()).find((s) => s.startsWith('linkbay_cookie_consent='));
            if (!c)
                return { necessary: true, analytics: false, marketing: false };
            return JSON.parse(decodeURIComponent(c.split('=')[1]));
        }
        catch (e) {
            return { necessary: true, analytics: false, marketing: false };
        }
    };
    next();
};
exports.cookieConsentMiddleware = cookieConsentMiddleware;
exports.default = exports.cookieConsentMiddleware;
