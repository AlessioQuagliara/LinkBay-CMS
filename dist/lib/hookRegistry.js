"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HookName = void 0;
var HookName;
(function (HookName) {
    HookName["PRODUCT_CREATED"] = "product.created";
    HookName["ORDER_PROCESSING"] = "order.processing";
    HookName["ADMIN_UI_EXTEND"] = "admin.ui.extend";
})(HookName || (exports.HookName = HookName = {}));
class HookRegistry {
    constructor() {
        this.localHandlers = new Map();
        this.sandboxHandlers = new Map();
    }
    registerLocal(hookName, pluginId, fn) {
        const list = this.localHandlers.get(hookName) || [];
        list.push({ pluginId, fn });
        this.localHandlers.set(hookName, list);
    }
    registerSandboxHandler(hookName, pluginId, sandbox, tenantId) {
        const list = this.sandboxHandlers.get(hookName) || [];
        list.push({ pluginId, sandbox, tenantId });
        this.sandboxHandlers.set(hookName, list);
    }
    async callHook(hookName, data, meta) {
        // run local handlers sequentially
        const local = this.localHandlers.get(hookName) || [];
        let current = data;
        for (const h of local) {
            try {
                const res = await Promise.resolve(h.fn(current, meta));
                // allow modification of data for processing hooks
                if (hookName === HookName.ORDER_PROCESSING && res !== undefined)
                    current = res;
            }
            catch (e) {
                console.error('local hook error', h.pluginId, e);
            }
        }
        // run sandbox handlers (each may be tenant-scoped)
        const sand = this.sandboxHandlers.get(hookName) || [];
        for (const s of sand) {
            // if tenantId in meta and handler has tenantId filter, skip mismatches
            if (s.tenantId != null && meta && meta.tenantId != null && String(s.tenantId) !== String(meta.tenantId))
                continue;
            try {
                const payload = { hook: hookName, data: current, meta };
                const resp = await s.sandbox.callHook(hookName, payload, meta);
                if (hookName === HookName.ORDER_PROCESSING && resp && resp.result && resp.result.modified) {
                    current = resp.result.modified;
                }
            }
            catch (e) {
                console.error('sandbox hook error', s.pluginId, e);
            }
        }
        return current;
    }
}
const registry = new HookRegistry();
exports.default = registry;
