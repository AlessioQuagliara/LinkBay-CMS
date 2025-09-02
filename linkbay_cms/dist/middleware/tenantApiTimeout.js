"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tenantApiTimeout = tenantApiTimeout;
const tenantResourceLimits_1 = require("../lib/tenantResourceLimits");
function tenantApiTimeout() {
    return (req, res, next) => {
        const plan = req.tenant && req.tenant.plan_type ? req.tenant.plan_type : 'free';
        const limits = (0, tenantResourceLimits_1.getPlanLimits)(plan);
        // set socket timeout for the response
        res.setTimeout(limits.apiTimeoutMs, () => {
            try {
                res.status(504).json({ error: 'request_timeout' });
            }
            catch (e) { }
        });
        next();
    };
}
