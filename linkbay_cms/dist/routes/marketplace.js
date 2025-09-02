"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const db_1 = require("../db");
const stripe_1 = __importDefault(require("stripe"));
const dotenv_1 = __importDefault(require("dotenv"));
const audit_1 = require("../middleware/audit");
dotenv_1.default.config();
const stripe = new stripe_1.default(process.env.STRIPE_SECRET_KEY || '', { apiVersion: '2022-11-15' });
const router = (0, express_1.Router)();
// Public: list all plugins
router.get('/plugins', async (req, res) => {
    try {
        // Show only plugins that have been approved in the central registry (available_plugins)
        // We join by name because the legacy `plugins` table uses a numeric id while the
        // registry uses a string id. This keeps the marketplace surface limited to approved items.
        const plugins = await db_1.knex('plugins as p')
            .join('available_plugins as ap', 'ap.name', 'p.name')
            .where('ap.is_approved', true)
            .select('p.*')
            .orderBy('p.created_at', 'desc');
        res.json({ success: true, plugins });
    }
    catch (err) {
        res.status(500).json({ error: 'server_error' });
    }
});
// Purchase a plugin: create a Checkout session that transfers funds to plugin creator
router.post('/purchase/:pluginId', (0, audit_1.logAuditEvent)('marketplace.purchase_initiated', (req) => ({ pluginId: req.params.pluginId, tenant: req && req.tenant && req.tenant.id })), async (req, res) => {
    const buyerTenant = req.tenant;
    if (!buyerTenant)
        return res.status(400).json({ error: 'tenant_required' });
    const pluginId = Number(req.params.pluginId);
    const plugin = await db_1.knex('plugins').where({ id: pluginId }).first();
    if (!plugin)
        return res.status(404).json({ error: 'plugin_not_found' });
    // Ensure the plugin has been approved in the central registry before purchase
    const approved = await db_1.knex('available_plugins').where({ name: plugin.name, is_approved: true }).first();
    if (!approved)
        return res.status(400).json({ error: 'plugin_not_approved' });
    if (!plugin.creator_tenant_id)
        return res.status(400).json({ error: 'plugin_has_no_creator' });
    // compute platform fee
    const price = plugin.price_cents || 0;
    const feePercent = Number(process.env.PLATFORM_FEE_PERCENT || '5');
    const appFee = Math.round(price * feePercent / 100);
    // find creator tenant and ensure stripe_connect_id exists
    const creator = await db_1.knex('tenants').where({ id: plugin.creator_tenant_id }).first();
    if (!creator || !creator.stripe_connect_id)
        return res.status(400).json({ error: 'creator_not_connected' });
    // create tenant_plugins pending record
    const inserted = await db_1.knex('tenant_plugins').insert({ tenant_id: buyerTenant.id, plugin_id: pluginId, status: 'pending' }).returning('*');
    const tenantPlugin = Array.isArray(inserted) ? inserted[0] : inserted;
    // create Checkout Session
    const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        mode: 'payment',
        line_items: [{ price_data: { currency: 'usd', product_data: { name: plugin.name }, unit_amount: price }, quantity: 1 }],
        payment_intent_data: {
            application_fee_amount: appFee,
            transfer_data: { destination: creator.stripe_connect_id }
        },
        metadata: { tenant_plugin_id: String(tenantPlugin.id), plugin_id: String(pluginId), tenant_id: String(buyerTenant.id) },
        success_url: `${req.headers.origin}/plugins/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${req.headers.origin}/plugins/cancel`
    }, { stripeAccount: creator.stripe_connect_id });
    // save session id for reconciliation
    await db_1.knex('tenant_plugins').where({ id: tenantPlugin.id }).update({ stripe_session_id: session.id });
    res.json({ url: session.url, id: session.id });
});
exports.default = router;
