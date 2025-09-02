"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const worker_threads_1 = require("worker_threads");
const path_1 = __importDefault(require("path"));
const { pluginPath, pluginId } = worker_threads_1.workerData;
function log(level, message, meta) { worker_threads_1.parentPort.postMessage({ type: 'log', level, message, meta }); }
let plugin = null;
try {
    // require the plugin in worker scope
    const resolved = path_1.default.resolve(pluginPath);
    plugin = require(resolved);
    plugin = plugin && (plugin.default || plugin);
}
catch (err) {
    log('error', 'failed to load plugin', err && err.message);
}
worker_threads_1.parentPort.on('message', async (msg) => {
    try {
        if (msg.type === 'register') {
            // provide a minimal context that is serializable
            const ctx = { pluginId, logger: { info: (m, meta) => log('info', String(m), meta), warn: (m, meta) => log('warn', String(m), meta), error: (m, meta) => log('error', String(m), meta) } };
            if (plugin && typeof plugin.register === 'function') {
                await plugin.register(ctx);
            }
            worker_threads_1.parentPort.postMessage({ id: msg.id, result: { ok: true } });
            return;
        }
        if (msg.type === 'registerHook') {
            const { hook } = msg.payload || {};
            // Inform main thread that this plugin wants to register a hook
            worker_threads_1.parentPort.postMessage({ type: 'registeredHook', hook });
            worker_threads_1.parentPort.postMessage({ id: msg.id, result: { ok: true } });
            return;
        }
        if (msg.type === 'registerRoute') {
            const { method, path } = msg.payload || {};
            // plugin should implement a handler registry; we'll assume plugin exports `routes` map
            worker_threads_1.parentPort.postMessage({ type: 'registeredRoute', method, path });
            worker_threads_1.parentPort.postMessage({ id: msg.id, result: { ok: true } });
            return;
        }
        if (msg.type === 'callRoute') {
            const { method, path, req } = msg.payload || {};
            try {
                const start = Date.now();
                let result = null;
                if (plugin && plugin.routes && typeof plugin.routes[path] === 'function') {
                    result = await plugin.routes[path](req);
                }
                else if (plugin && plugin.default && typeof plugin.default.routes === 'object' && typeof plugin.default.routes[path] === 'function') {
                    result = await plugin.default.routes[path](req);
                }
                else {
                    worker_threads_1.parentPort.postMessage({ id: msg.id, error: 'route_not_found' });
                    return;
                }
                const duration = Date.now() - start;
                // emit structured log about route execution
                worker_threads_1.parentPort.postMessage({ type: 'log', level: 'info', message: `route_executed`, meta: { method, path, duration_ms: duration } });
                worker_threads_1.parentPort.postMessage({ id: msg.id, result, meta: { duration_ms: duration } });
            }
            catch (e) {
                worker_threads_1.parentPort.postMessage({ id: msg.id, error: e && e.message ? String(e.message) : 'error' });
            }
            return;
        }
        if (msg.type === 'callHook') {
            const { hook, payload } = msg.payload || {};
            const start = Date.now();
            try {
                if (plugin && plugin.hooks && typeof plugin.hooks[hook] === 'function') {
                    await plugin.hooks[hook](payload);
                }
                const duration = Date.now() - start;
                worker_threads_1.parentPort.postMessage({ type: 'log', level: 'info', message: 'hook_executed', meta: { hook, duration_ms: duration } });
                worker_threads_1.parentPort.postMessage({ id: msg.id, result: { ok: true }, meta: { duration_ms: duration } });
            }
            catch (e) {
                worker_threads_1.parentPort.postMessage({ id: msg.id, error: e && e.message ? String(e.message) : 'error' });
            }
            return;
        }
        if (msg.type === 'ping') {
            worker_threads_1.parentPort.postMessage({ id: msg.id, result: 'pong' });
            return;
        }
    }
    catch (err) {
        worker_threads_1.parentPort.postMessage({ id: msg.id, error: err && err.message ? String(err.message) : 'error' });
    }
});
// signal ready
worker_threads_1.parentPort.postMessage({ type: 'ready' });
