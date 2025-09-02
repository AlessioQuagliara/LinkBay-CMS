"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const db_1 = require("../db");
const router = express_1.default.Router();
// admin-only: show tenant usage
router.get('/', async (req, res) => {
    const tenantId = req.tenant && req.tenant.id ? req.tenant.id : req.headers['x-tenant-id'];
    if (!tenantId)
        return res.status(400).json({ error: 'no_tenant' });
    const tenant = await (0, db_1.knex)('tenants').where({ id: tenantId }).first();
    if (!tenant)
        return res.status(404).json({ error: 'tenant_not_found' });
    const [{ total }] = await (0, db_1.knex)('media').where({ tenant_id: tenantId }).sum('size_bytes as total');
    const storageUsed = Number(total || 0);
    const bandwidth = Number(tenant.monthly_bandwidth_bytes || 0);
    res.json({ tenant: tenantId, storageQuota: tenant.storage_quota_bytes || null, storageUsed, monthlyBandwidthUsed: bandwidth });
});
exports.default = router;
