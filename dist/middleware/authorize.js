"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.authorize = void 0;
const authorize = (roles) => {
    const allowed = Array.isArray(roles) ? roles : [roles];
    return (req, res, next) => {
        const user = req.user;
        if (!user)
            return res.status(401).json({ error: 'not_authenticated' });
        if (!allowed.includes(user.role))
            return res.status(403).json({ error: 'forbidden' });
        next();
    };
};
exports.authorize = authorize;
