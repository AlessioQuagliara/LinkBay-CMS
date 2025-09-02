"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BasicEventBus = void 0;
class BasicEventBus {
    constructor() {
        this.handlers = {};
    }
    on(eventType, handler) {
        this.handlers[eventType] = this.handlers[eventType] || [];
        this.handlers[eventType].push(handler);
    }
    off(eventType, handler) {
        const list = this.handlers[eventType] || [];
        this.handlers[eventType] = list.filter(h => h !== handler);
    }
    emit(evt) {
        // call specific handlers
        const list = this.handlers[evt.type] || [];
        for (const h of list) {
            try {
                h(evt);
            }
            catch (e) { /* swallow */ }
        }
        // call wildcard handlers
        const wild = this.handlers['*'] || [];
        for (const h of wild) {
            try {
                h(evt);
            }
            catch (e) { /* swallow */ }
        }
    }
}
exports.BasicEventBus = BasicEventBus;
// singleton instance for app
const eventBus = new BasicEventBus();
exports.default = eventBus;
