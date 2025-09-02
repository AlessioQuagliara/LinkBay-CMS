"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.WebhookConsumer = void 0;
const eventBus_1 = __importDefault(require("./eventBus"));
const node_fetch_1 = __importDefault(require("node-fetch"));
const crypto_1 = __importDefault(require("crypto"));
const db_1 = require("../db");
function sleep(ms) { return new Promise(res => setTimeout(res, ms)); }
class WebhookConsumer {
    constructor() {
        this.registered = false;
        this.handler = this.handleEvent.bind(this);
    }
    start() {
        if (this.registered)
            return;
        // subscribe to all events; we'll filter per-tenant webhooks
        eventBus_1.default.on('*', this.handler);
        this.registered = true;
    }
    stop() {
        if (!this.registered)
            return;
        eventBus_1.default.off('*', this.handler);
        this.registered = false;
    }
    async handleEvent(evt) {
        try {
            const tenantId = evt.tenant_id || null;
            if (!tenantId)
                return; // only tenant-scoped events
            // find active webhooks for tenant
            const hooks = await (0, db_1.knex)('tenant_webhooks').where({ tenant_id: tenantId, is_active: true }).select('*');
            for (const h of hooks) {
                const types = h.event_types ? (Array.isArray(h.event_types) ? h.event_types : JSON.parse(h.event_types)) : null;
                if (types && types.length && !types.includes(evt.type))
                    continue;
                // send webhook asynchronously (don't block the bus)
                this.sendWithRetry(h, evt).catch((err) => { console.error('webhook send failed', err && err.message); });
            }
        }
        catch (err) {
            console.error('webhook handler error', err && err.message);
        }
    }
    async sendWithRetry(hook, evt, attempt = 0) {
        const maxAttempts = 5;
        try {
            await this.sendOnce(hook, evt, attempt);
            // log success
            await (0, db_1.knex)('webhook_logs').insert({ tenant_id: hook.tenant_id, webhook_id: hook.id, event_type: evt.type, event_payload: JSON.stringify(evt), success: true, attempts: attempt + 1, response_status: 'ok' });
        }
        catch (err) {
            const nextAttempt = attempt + 1;
            await (0, db_1.knex)('webhook_logs').insert({ tenant_id: hook.tenant_id, webhook_id: hook.id, event_type: evt.type, event_payload: JSON.stringify(evt), success: false, attempts: nextAttempt, error: String(err && err.message || err) });
            if (nextAttempt < maxAttempts) {
                const backoff = Math.min(30000, 200 * Math.pow(2, attempt));
                await sleep(backoff);
                return this.sendWithRetry(hook, evt, nextAttempt);
            }
        }
    }
    async sendOnce(hook, evt, attempt) {
        const payload = { event: evt.type, data: evt, attempt };
        const body = JSON.stringify(payload);
        const headers = { 'Content-Type': 'application/json' };
        if (hook.secret) {
            const sig = crypto_1.default.createHmac('sha256', String(hook.secret)).update(body).digest('hex');
            headers['X-LinkBay-Signature'] = sig;
        }
        const res = await (0, node_fetch_1.default)(hook.url, { method: 'POST', body, headers, timeout: 10000 });
        if (!res.ok)
            throw new Error('webhook_response_' + res.status);
    }
}
exports.WebhookConsumer = WebhookConsumer;
const defaultConsumer = new WebhookConsumer();
if (process.env.NODE_ENV !== 'test') {
    try {
        defaultConsumer.start();
    }
    catch (e) { }
}
// graceful teardown
process.on('exit', () => { try {
    defaultConsumer.stop();
}
catch (e) { } });
exports.default = defaultConsumer;
