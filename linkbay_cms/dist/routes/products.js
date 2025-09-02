"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const dbMultiTenant_1 = require("../dbMultiTenant");
const cache_1 = __importStar(require("../cache"));
const eventBus_1 = __importDefault(require("../lib/eventBus"));
const router = (0, express_1.Router)();
// Helper to load products with variants (for a given subset)
async function loadProductsWithVariants(k, productRows) {
    const productIds = productRows.map((p) => p.id);
    const variants = productIds.length ? await k('product_variants').whereIn('product_id', productIds).select('*') : [];
    const attributes = variants.length ? await k('variant_attributes').whereIn('variant_id', variants.map((v) => v.id)).select('*') : [];
    const variantsByProduct = {};
    variants.forEach((v) => { variantsByProduct[v.product_id] = variantsByProduct[v.product_id] || []; variantsByProduct[v.product_id].push(v); });
    const attributesByVariant = {};
    attributes.forEach((a) => { attributesByVariant[a.variant_id] = attributesByVariant[a.variant_id] || []; attributesByVariant[a.variant_id].push(a); });
    return productRows.map((p) => ({ ...p, variants: (variantsByProduct[p.id] || []).map((v) => ({ ...v, attributes: attributesByVariant[v.id] || [] })) }));
}
// GET /api/products
// Supports JSON (default) and HTMX partial rendering with ?partial=table&page=N
router.get('/', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    // HTMX table partial + pagination
    if (req.query.partial === 'table') {
        const page = Math.max(1, Number(req.query.page) || 1);
        const perPage = Math.max(10, Number(req.query.per_page) || 20);
        const offset = (page - 1) * perPage;
        const [products, countRow] = await Promise.all([
            k('products').select('*').limit(perPage).offset(offset),
            k('products').count('* as cnt').first()
        ]);
        const total = Number(countRow && countRow.cnt || 0);
        const nextPage = offset + products.length < total;
        const rows = await loadProductsWithVariants(k, products);
        // if first page, render full table wrapper, else render just rows to append
        if (page === 1)
            return res.render('products/partials/table', { rows, page, perPage, nextPage });
        return res.render('products/partials/rows', { rows, page, perPage, nextPage });
    }
    // default JSON API (cached)
    const key = (0, cache_1.cacheKeyForQuery)(tenant.id, 'products:all:with_variants');
    const rows = await cache_1.default.cached(key, async () => {
        const products = await k('products').select('*');
        return await loadProductsWithVariants(k, products);
    }, 120);
    res.json(rows);
});
// GET /api/products/new?partial=form - returns form partial
router.get('/new', async (req, res) => {
    if (req.query.partial === 'form')
        return res.render('partials/product-form', { product: null });
    res.status(400).json({ error: 'bad_request' });
});
// GET /api/products/:id?partial=row - return a single row partial or json
router.get('/:id', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const id = Number(req.params.id);
    const product = await k('products').where({ id }).first();
    if (!product)
        return res.status(404).json({ error: 'not_found' });
    if (req.query.partial === 'row') {
        const rows = await loadProductsWithVariants(k, [product]);
        return res.render('products/partials/row', { p: rows[0] });
    }
    res.json(product);
});
// DELETE /api/products/:id - support HTMX delete
router.delete('/:id', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const id = Number(req.params.id);
    await k('product_variants').where({ product_id: id }).del();
    await k('products').where({ id }).del();
    // return HTMX snippet to refresh table
    return res.send('<div class="p-2 text-sm text-green-800 bg-green-50 rounded">Prodotto eliminato</div><script>htmx.trigger(document.querySelector(\"#products-table\"), \"refresh\")</script>');
});
// product detail
router.get('/:id', async (req, res) => {
    const tenant = req.tenant;
    if (!tenant)
        return res.status(404).json({ error: 'tenant_required' });
    const k = req.getTenantDB ? await req.getTenantDB() : (0, dbMultiTenant_1.getTenantDB)(tenant.id);
    const id = Number(req.params.id);
    const product = await k('products').where({ id }).first();
    if (!product)
        return res.status(404).json({ error: 'not_found' });
    // fetch variants
    const variants = await k('product_variants').where({ product_id: id }).select('*');
    try {
        eventBus_1.default.emit({ type: 'ProductViewed', tenant_id: tenant.id, product_id: id, user_id: req.user ? req.user.id : null, timestamp: new Date().toISOString() });
    }
    catch (e) { }
    res.json({ ...product, variants });
});
exports.default = router;
