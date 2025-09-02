"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.trackBandwidth = void 0;
const db_1 = require("../db");
const trackBandwidth = (req, res, next) => {
    const tenantId = req.tenant && req.tenant.id ? req.tenant.id : req.headers['x-tenant-id'];
    if (!tenantId)
        return next();
    let bytes = 0;
    const origWrite = res.write;
    const origEnd = res.end;
    res.write = function (chunk, encoding, cb) {
        try {
            if (chunk)
                bytes += Buffer.byteLength(typeof chunk === 'string' ? chunk : chunk instanceof Buffer ? chunk : JSON.stringify(chunk));
        }
        catch (e) { }
        return origWrite.apply(res, arguments);
    };
    res.end = function (chunk, encoding, cb) {
        try {
            if (chunk)
                bytes += Buffer.byteLength(typeof chunk === 'string' ? chunk : chunk instanceof Buffer ? chunk : JSON.stringify(chunk));
        }
        catch (e) { }
        try {
            if (bytes > 0)
                (0, db_1.knex)('tenants').where({ id: tenantId }).increment('monthly_bandwidth_bytes', Number(bytes));
        }
        catch (e) { }
        return origEnd.apply(res, arguments);
    };
    next();
};
exports.trackBandwidth = trackBandwidth;
