"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.default = tenantResolver;
async function tenantResolver(req, res, next) {
    // Simple subdomain resolver - adjust to your needs
    const host = req.headers.host || '';
    const subdomain = host.split(':')[0].split('.')[0] || 'default';
    // Attach a minimal tenant object to the request for downstream handlers
    req.tenant = { subdomain };
    next();
}
