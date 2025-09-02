"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
class SimpleCache {
    constructor() {
        this.store = new Map();
    }
    get(key) {
        const e = this.store.get(key);
        if (!e)
            return null;
        if (Date.now() > e.expiresAt) {
            this.store.delete(key);
            return null;
        }
        return e.value;
    }
    set(key, value, ttlSeconds = 30) {
        const expiresAt = Date.now() + ttlSeconds * 1000;
        this.store.set(key, { value, expiresAt });
    }
    del(key) {
        this.store.delete(key);
    }
}
exports.default = new SimpleCache();
