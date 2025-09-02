import { parentPort, workerData } from 'worker_threads';
import path from 'path';

type Msg = { id?: string; type: string; payload?: any };

const { pluginPath, pluginId } = workerData as any;

function log(level:string, message:string, meta?:any) { parentPort!.postMessage({ type: 'log', level, message, meta }); }

let plugin: any = null;

try {
  // require the plugin in worker scope
  const resolved = path.resolve(pluginPath);
  plugin = require(resolved);
  plugin = plugin && (plugin.default || plugin);
} catch (err:any) {
  log('error', 'failed to load plugin', err && err.message);
}

parentPort!.on('message', async (msg: Msg) => {
  try {
  if (msg.type === 'register') {
      // provide a minimal context that is serializable
  const ctx = { pluginId, logger: { info: (m:any, meta?:any) => log('info', String(m), meta), warn: (m:any, meta?:any) => log('warn', String(m), meta), error: (m:any, meta?:any) => log('error', String(m), meta) } };
      if (plugin && typeof plugin.register === 'function') {
        await plugin.register(ctx);
      }
      parentPort!.postMessage({ id: msg.id, result: { ok: true } });
      return;
    }

    if (msg.type === 'registerHook') {
      const { hook } = msg.payload || {};
      // Inform main thread that this plugin wants to register a hook
      parentPort!.postMessage({ type: 'registeredHook', hook });
      parentPort!.postMessage({ id: msg.id, result: { ok: true } });
      return;
    }

    if (msg.type === 'registerRoute') {
      const { method, path } = msg.payload || {};
      // plugin should implement a handler registry; we'll assume plugin exports `routes` map
      parentPort!.postMessage({ type: 'registeredRoute', method, path });
      parentPort!.postMessage({ id: msg.id, result: { ok: true } });
      return;
    }

    if (msg.type === 'callRoute') {
      const { method, path, req } = msg.payload || {};
      try {
        const start = Date.now();
        let result: any = null;
        if (plugin && plugin.routes && typeof plugin.routes[path] === 'function') {
          result = await plugin.routes[path](req);
        } else if (plugin && plugin.default && typeof plugin.default.routes === 'object' && typeof plugin.default.routes[path] === 'function') {
          result = await plugin.default.routes[path](req);
        } else {
          parentPort!.postMessage({ id: msg.id, error: 'route_not_found' });
          return;
        }
        const duration = Date.now() - start;
        // emit structured log about route execution
        parentPort!.postMessage({ type: 'log', level: 'info', message: `route_executed`, meta: { method, path, duration_ms: duration } });
        parentPort!.postMessage({ id: msg.id, result, meta: { duration_ms: duration } });
      } catch (e:any) { parentPort!.postMessage({ id: msg.id, error: e && e.message ? String(e.message) : 'error' }); }
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
        parentPort!.postMessage({ type: 'log', level: 'info', message: 'hook_executed', meta: { hook, duration_ms: duration } });
        parentPort!.postMessage({ id: msg.id, result: { ok: true }, meta: { duration_ms: duration } });
      } catch (e:any) {
        parentPort!.postMessage({ id: msg.id, error: e && e.message ? String(e.message) : 'error' });
      }
      return;
    }

    if (msg.type === 'ping') { parentPort!.postMessage({ id: msg.id, result: 'pong' }); return; }
  } catch (err:any) {
    parentPort!.postMessage({ id: msg.id, error: err && err.message ? String(err.message) : 'error' });
  }
});

// signal ready
parentPort!.postMessage({ type: 'ready' });
