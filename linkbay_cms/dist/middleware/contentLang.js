"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.contentLang = void 0;
const supported = ['en', 'it', 'es'];
const contentLang = (req, res, next) => {
    // prefer explicit query param
    const q = (req.query.lang || '');
    if (q && supported.includes(q)) {
        req.contentLang = q;
        return next();
    }
    // detect from URL prefix: /en/slug or /it/...
    const m = req.path.match(/^\/(en|it|es)(?:\/|$)/);
    if (m) {
        req.contentLang = m[1];
    }
    else {
        req.contentLang = 'en';
    }
    next();
};
exports.contentLang = contentLang;
