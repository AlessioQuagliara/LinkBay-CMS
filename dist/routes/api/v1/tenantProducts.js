"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../../../db");
const requireApiKey_1 = require("../../../middleware/requireApiKey");
const router = (0, express_1.Router)();
// All routes under here require a valid API key
router.use(requireApiKey_1.requireApiKey);
/**
 * GET /api/v1/tenant/products
 * @summary List products for tenant
 * @return {array} 200 - products
 */
router.get('/products', (0, requireApiKey_1.requireScope)('products:read'), async (req, res) => {
    try {
        const tenantId = req.tenant.id;
        // tenant-specific products assumed to be in tenant schema or have tenant_id
        const products = await (0, db_1.knex)('products').where('tenant_id', tenantId).select('*').limit(100);
        res.json(products);
    }
    catch (err) {
        res.status(500).json({ error: 'server_error' });
    }
});
/**
 * POST /api/v1/tenant/products
 * @summary Create a product
 * @param {object} request.body.required - product body
 */
router.post('/products', (0, requireApiKey_1.requireScope)('products:write'), async (req, res) => {
    try {
        const tenantId = req.tenant.id;
        const body = req.body || {};
        // minimal validation
        if (!body.name || !body.price_cents)
            return res.status(400).json({ error: 'name_and_price_required' });
        const [id] = await (0, db_1.knex)('products').insert({ tenant_id: tenantId, name: body.name, description: body.description || null, price_cents: body.price_cents, created_at: new Date() }).returning('id');
        res.status(201).json({ id });
    }
    catch (err) {
        console.error('api create product', err);
        res.status(500).json({ error: 'server_error' });
    }
});
exports.default = router;
