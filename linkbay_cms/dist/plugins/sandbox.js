"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.PluginSandbox = void 0;
const worker_threads_1 = require("worker_threads");
const path_1 = __importDefault(require("path"));
const db_1 = require("../db");
class PluginSandbox {
    constructor(pluginPath, pluginId) {
        this.pending = new Map();
        this.ready = false;
        this.pluginPath = pluginPath;
        this.pluginId = pluginId;
    }
    start() {
        return new Promise((resolve, reject) => {
            const workerFile = path_1.default.join(__dirname, 'pluginWorker.js');
            this.worker = new worker_threads_1.Worker(workerFile, { workerData: { pluginPath: this.pluginPath, pluginId: this.pluginId } });
            this.worker.on('message', (msg) => this.handleMessage(msg));
            this.worker.on('error', (err) => {
                console.error('plugin worker error', this.pluginId, err);
            });
            this.worker.on('exit', (code) => {
                this.ready = false;
                if (code !== 0)
                    console.warn('plugin worker exited', this.pluginId, code);
            });
            const t = setTimeout(() => {
                if (!this.ready)
                    return reject(new Error('plugin worker start timeout'));
            }, 3000);
            // resolve when worker signals ready
            const onReady = (msg) => {
                if (msg && msg.type === 'ready') {
                    this.ready = true;
                    this.worker.off('message', onReady);
                    clearTimeout(t);
                    resolve();
                }
            };
            this.worker.on('message', onReady);
        });
    }
    stop() {
        try {
            this.worker && this.worker.terminate();
        }
        catch (e) { }
        this.pending.forEach(p => p.reject(new Error('sandbox stopped')));
        this.pending.clear();
    }
    handleMessage(msg) {
        if (!msg || !msg.type)
            return;
        if (msg.type === 'log') {
            const level = msg.level || 'info';
            const message = msg.message || '';
            const meta = msg.meta || null;
            const duration = (meta && (meta.duration_ms || meta.duration)) ? (meta.duration_ms || meta.duration) : null;
            // mirror to console
            if (level === 'debug')
                console.debug(`[plugin:${this.pluginId}]`, message, meta);
            else if (level === 'warn')
                console.warn(`[plugin:${this.pluginId}]`, message, meta);
            else if (level === 'error')
                console.error(`[plugin:${this.pluginId}]`, message, meta);
            else
                console.info(`[plugin:${this.pluginId}]`, message, meta);
            // persist to DB (best-effort)
            try {
                (0, db_1.knex)('plugin_logs').insert({ plugin_id: this.pluginId, tenant_id: null, level, message: String(message || ''), meta: meta ? meta : null, duration_ms: duration, created_at: new Date() }).catch(() => { });
            }
            catch (e) { }
            return;
        }
        if (msg.type === 'registeredHook') {
            // informational
            console.info(`[plugin:${this.pluginId}] registered hook`, msg.hook, 'tenant', msg.tenantId);
            return;
        }
        if (msg.id) {
            const pending = this.pending.get(msg.id);
            if (!pending)
                return;
            this.pending.delete(msg.id);
            if (msg.error)
                pending.reject(new Error(msg.error));
            else
                pending.resolve(msg.result);
        }
    }
    sendRequest(action, payload) {
        if (!this.worker)
            return Promise.reject(new Error('worker-not-started'));
        const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
        const msg = { id, type: action, payload };
        return new Promise((resolve, reject) => {
            this.pending.set(id, { resolve, reject });
            try {
                this.worker.postMessage(msg);
            }
            catch (e) {
                this.pending.delete(id);
                reject(e);
            }
            setTimeout(() => { if (this.pending.has(id)) {
                this.pending.delete(id);
                reject(new Error('request-timeout'));
            } }, 10000);
        });
    }
    register(tenantId, context) {
        return this.sendRequest('register', { tenantId, context });
    }
    registerHook(hookName) {
        return this.sendRequest('registerHook', { hook: hookName });
    }
    registerRoute(method, routePath) {
        return this.sendRequest('registerRoute', { method, path: routePath });
    }
    callRoute(method, routePath, req) {
        return this.sendRequest('callRoute', { method, path: routePath, req });
    }
    callHook(hook, payload, meta) {
        return this.sendRequest('callHook', { hook, payload, meta });
    }
}
exports.PluginSandbox = PluginSandbox;
exports.default = PluginSandbox;
