import { Worker } from 'worker_threads';
import path from 'path';
import { knex } from '../db';

type Pending = { resolve: (v:any)=>void, reject:(e:any)=>void };

export class PluginSandbox {
  private worker?: Worker;
  private pending: Map<string, Pending> = new Map();
  private ready = false;
  private pluginPath: string;
  readonly pluginId: string;

  constructor(pluginPath: string, pluginId: string) {
    this.pluginPath = pluginPath;
    this.pluginId = pluginId;
  }

  start(): Promise<void> {
    return new Promise((resolve, reject) => {
      const workerFile = path.join(__dirname, 'pluginWorker.js');
      this.worker = new Worker(workerFile, { workerData: { pluginPath: this.pluginPath, pluginId: this.pluginId } });
      this.worker.on('message', (msg:any) => this.handleMessage(msg));
      this.worker.on('error', (err) => {
        console.error('plugin worker error', this.pluginId, err);
      });
      this.worker.on('exit', (code) => {
        this.ready = false;
        if (code !== 0) console.warn('plugin worker exited', this.pluginId, code);
      });

      const t = setTimeout(() => {
        if (!this.ready) return reject(new Error('plugin worker start timeout'));
      }, 3000);

      // resolve when worker signals ready
      const onReady = (msg:any) => {
        if (msg && msg.type === 'ready') {
          this.ready = true;
          this.worker!.off('message', onReady);
          clearTimeout(t);
          resolve();
        }
      };
      this.worker.on('message', onReady);
    });
  }

  stop() {
    try { this.worker && this.worker.terminate(); } catch (e) {}
    this.pending.forEach(p => p.reject(new Error('sandbox stopped')));
    this.pending.clear();
  }

  private handleMessage(msg:any) {
    if (!msg || !msg.type) return;
    if (msg.type === 'log') {
      const level = msg.level || 'info';
      const message = msg.message || '';
      const meta = msg.meta || null;
      const duration = (meta && (meta.duration_ms || meta.duration)) ? (meta.duration_ms || meta.duration) : null;
      // mirror to console
      if (level === 'debug') console.debug(`[plugin:${this.pluginId}]`, message, meta);
      else if (level === 'warn') console.warn(`[plugin:${this.pluginId}]`, message, meta);
      else if (level === 'error') console.error(`[plugin:${this.pluginId}]`, message, meta);
      else console.info(`[plugin:${this.pluginId}]`, message, meta);
      // persist to DB (best-effort)
      try {
        knex('plugin_logs').insert({ plugin_id: this.pluginId, tenant_id: null, level, message: String(message || ''), meta: meta ? meta : null, duration_ms: duration, created_at: new Date() }).catch(()=>{});
      } catch (e) {}
      return;
    }
    if (msg.type === 'registeredHook') {
      // informational
      console.info(`[plugin:${this.pluginId}] registered hook`, msg.hook, 'tenant', msg.tenantId);
      return;
    }
    if (msg.id) {
      const pending = this.pending.get(msg.id);
      if (!pending) return;
      this.pending.delete(msg.id);
      if (msg.error) pending.reject(new Error(msg.error)); else pending.resolve(msg.result);
    }
  }

  private sendRequest(action:string, payload:any): Promise<any> {
    if (!this.worker) return Promise.reject(new Error('worker-not-started'));
    const id = `${Date.now()}-${Math.random().toString(36).slice(2,9)}`;
    const msg = { id, type: action, payload };
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      try { this.worker!.postMessage(msg); } catch (e) { this.pending.delete(id); reject(e); }
      setTimeout(() => { if (this.pending.has(id)) { this.pending.delete(id); reject(new Error('request-timeout')); } }, 10000);
    });
  }

  register(tenantId: number | string | null, context: any) {
    return this.sendRequest('register', { tenantId, context });
  }

  registerHook(hookName: string) {
    return this.sendRequest('registerHook', { hook: hookName });
  }

  registerRoute(method: string, routePath: string) {
    return this.sendRequest('registerRoute', { method, path: routePath });
  }

  callRoute(method: string, routePath: string, req: any) {
    return this.sendRequest('callRoute', { method, path: routePath, req });
  }

  callHook(hook: string, payload: any, meta: any) {
    return this.sendRequest('callHook', { hook, payload, meta });
  }
}

export default PluginSandbox;
