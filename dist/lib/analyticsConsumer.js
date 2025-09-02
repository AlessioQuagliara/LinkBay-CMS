"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DatabaseAnalyticsConsumer = exports.analyticsKnex = void 0;
const knex_1 = __importDefault(require("knex"));
const eventBus_1 = __importDefault(require("./eventBus"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const ANALYTICS_DB_URL = process.env.ANALYTICS_DATABASE_URL || process.env.DATABASE_URL;
// separate knex instance / pool for analytics
exports.analyticsKnex = (0, knex_1.default)({ client: 'pg', connection: ANALYTICS_DB_URL, pool: { min: 0, max: 5 } });
function sleep(ms) { return new Promise(res => setTimeout(res, ms)); }
class DatabaseAnalyticsConsumer {
    constructor() {
        this.registered = false;
        this.handler = this.handleEvent.bind(this);
    }
    start() {
        if (this.registered)
            return;
        // subscribe to all analytic events
        eventBus_1.default.on('*', this.handler);
        // also subscribe to specific types for efficiency
        ['PageView', 'ProductViewed', 'AddToCart', 'CheckoutStarted', 'PurchaseCompleted', 'UserLoggedIn'].forEach(t => eventBus_1.default.on(t, this.handler));
        this.registered = true;
    }
    stop() {
        if (!this.registered)
            return;
        eventBus_1.default.off('*', this.handler);
        ['PageView', 'ProductViewed', 'AddToCart', 'CheckoutStarted', 'PurchaseCompleted', 'UserLoggedIn'].forEach(t => eventBus_1.default.off(t, this.handler));
        this.registered = false;
    }
    async handleEvent(evt) {
        try {
            await this.saveEventWithRetry(evt);
        }
        catch (err) {
            // last-resort: log but don't crash the app
            try {
                console.error('analytics save failed', err.message || err);
            }
            catch (e) { }
        }
    }
    async saveEventWithRetry(evt, attempts = 0) {
        const maxAttempts = 5;
        try {
            await this.saveEvent(evt);
        }
        catch (err) {
            const retriable = (err && err.code && ['57P01', '57P03', '53300', 'ECONNRESET', 'ETIMEDOUT'].includes(err.code)) || attempts < 3;
            if (retriable && attempts < maxAttempts) {
                const backoff = Math.min(2000, 100 * Math.pow(2, attempts));
                await sleep(backoff);
                return this.saveEventWithRetry(evt, attempts + 1);
            }
            throw err;
        }
    }
    async saveEvent(evt) {
        // Map our events to analytics.events columns
        const common = {
            tenant_id: evt.tenant_id || null,
            event_type: evt.type ? String(evt.type).toLowerCase() : 'unknown',
            event_data: {},
            user_id: evt.user_id || null,
            session_id: evt.session_id || null,
            url_path: evt.path || evt.url_path || null,
            timestamp: evt && evt.timestamp ? new Date(evt.timestamp) : new Date()
        };
        // populate event_data with the whole event payload minus duplicated fields
        const payload = { ...evt };
        delete payload.type;
        delete payload.tenant_id;
        delete payload.user_id;
        delete payload.session_id;
        delete payload.path;
        delete payload.url_path;
        delete payload.timestamp;
        common.event_data = payload;
        await (0, exports.analyticsKnex)('analytics.events').insert({
            tenant_id: common.tenant_id,
            event_type: common.event_type,
            event_data: JSON.stringify(common.event_data),
            user_id: common.user_id,
            session_id: common.session_id,
            url_path: common.url_path,
            timestamp: common.timestamp
        });
    }
}
exports.DatabaseAnalyticsConsumer = DatabaseAnalyticsConsumer;
// default instance and auto-start in development
const defaultConsumer = new DatabaseAnalyticsConsumer();
if (process.env.NODE_ENV !== 'test') {
    try {
        defaultConsumer.start();
    }
    catch (e) { /* ignore startup errors */ }
}
// graceful shutdown: destroy analytics pool on process exit
process.on('exit', () => { try {
    exports.analyticsKnex.destroy();
}
catch (e) { } });
process.on('SIGINT', () => { try {
    exports.analyticsKnex.destroy();
}
catch (e) { } process.exit(0); });
exports.default = defaultConsumer;
