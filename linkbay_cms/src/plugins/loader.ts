import fs from 'fs';
import path from 'path';
import vm from 'vm';
import PluginSandbox from './sandbox';
import { knex } from '../db';
import eventBus from '../lib/eventBus';
import hookRegistry from '../lib/hookRegistry';
import defaultConsumer from '../lib/analyticsConsumer';
import { LinkBayPlugin, PluginContext, PluginLogger } from './types';
import { knex as knexClient } from '../db';
import { registerPluginRoute } from './router';
import pkg from '../../package.json';

const CORE_VERSION = (pkg && (pkg as any).version) ? String((pkg as any).version) : '0.0.0';

function compareSemver(a:string, b:string) {
  const pa = a.split('.').map(x=>Number(x||0));
  const pb = b.split('.').map(x=>Number(x||0));
  for (let i=0;i<3;i++){ if (pa[i] > pb[i]) return 1; if (pa[i] < pb[i]) return -1; }
  return 0;
}

function satisfiesCore(versionRange: string | undefined, coreVersion: string) {
  if (!versionRange) return true;
  const v = coreVersion;
  if (versionRange.startsWith('^')) {
    const base = versionRange.slice(1);
    const major = Number(base.split('.')[0] || 0);
    const upper = String((major+1)+'.0.0');
    return compareSemver(v, base) >= 0 && compareSemver(v, upper) < 0;
  }
  if (versionRange.startsWith('>=')) return compareSemver(v, versionRange.slice(2)) >= 0;
  if (versionRange.startsWith('<=')) return compareSemver(v, versionRange.slice(2)) <= 0;
  if (versionRange.startsWith('>')) return compareSemver(v, versionRange.slice(1)) > 0;
  if (versionRange.startsWith('<')) return compareSemver(v, versionRange.slice(1)) < 0;
  return compareSemver(v, versionRange) === 0;
}

const PLUGINS_DIR = path.join(__dirname, '..', '..', 'plugins');

function makeLogger(pluginId: string): PluginLogger {
  return {
    debug: async (...args:any[]) => {
      console.debug(`[plugin:${pluginId}]`, ...args);
      try { await knexClient('plugin_logs').insert({ plugin_id: pluginId, level: 'debug', message: String(args[0] || ''), meta: { args }, created_at: new Date() }); } catch(e){}
    },
    info: async (...args:any[]) => {
      console.info(`[plugin:${pluginId}]`, ...args);
      try { await knexClient('plugin_logs').insert({ plugin_id: pluginId, level: 'info', message: String(args[0] || ''), meta: { args }, created_at: new Date() }); } catch(e){}
    },
    warn: async (...args:any[]) => {
      console.warn(`[plugin:${pluginId}]`, ...args);
      try { await knexClient('plugin_logs').insert({ plugin_id: pluginId, level: 'warn', message: String(args[0] || ''), meta: { args }, created_at: new Date() }); } catch(e){}
    },
    error: async (...args:any[]) => {
      console.error(`[plugin:${pluginId}]`, ...args);
      try { await knexClient('plugin_logs').insert({ plugin_id: pluginId, level: 'error', message: String(args[0] || ''), meta: { args }, created_at: new Date() }); } catch(e){}
    },
  };
}

// Minimal PluginContext factory - the core must ensure this surface is safe
function makeContext(pluginId: string): PluginContext {
  const logger = makeLogger(pluginId);

  // Simple settings backed by tenant_plugins.config when used per-tenant
  const settings = {
    async get(key: string) { return null; },
    async set(key: string, value: any) { /* noop here - persistence done on register per tenant */ }
  };

  // Hook registrar - register handlers on the app eventBus
  const hooks = {
    register<T = any>(hook: any, handler: (payload:T, meta:{ tenantId?: string | null }) => void | Promise<void>) {
      // wrap handler to prevent throwing into core
      eventBus.on(hook, async (evt:any) => {
        try { await handler(evt, { tenantId: (evt as any).tenant_id || null }); } catch (e) { logger.error('hook handler failed', e); }
      });
    }
  };

  // Minimal API router stub: core should mount routes under /_plugins/:id
  const api = {
    registerRoute: (method:string, routePath:string, handler: any) => {
      // validate routePath
      const safe = routePath.startsWith('/') ? routePath : '/' + routePath;
      // mount into core router; since this is in-process we call handler directly
      registerPluginRoute(pluginId, method, safe, async ({ method, path, req }) => {
        try {
          const res = await Promise.resolve(handler(req));
          return { status: 200, body: res };
        } catch (e:any) { return { status: 500, body: { error: 'plugin_handler_error' } }; }
      });
    }
  } as any;

  const admin = { registerPanel: (_id:string, _label:string, _mountPath:string) => logger.info('admin panel registered', _id, _mountPath) };
  const editor = { registerBlock: (_d:any) => logger.info('editor block registered', _d && _d.id) };

  const ctx: PluginContext = {
    pluginId,
    logger,
    hooks,
    api,
    admin,
    editor,
    settings
  };

  return ctx;
}

// Load plugin code from file path. Use vm.Script to evaluate in isolated context when possible.
function loadPluginFromFile(filePath: string): LinkBayPlugin | null {
  const code = fs.readFileSync(filePath, 'utf8');
  try {
    // Run in a limited VM context exposing only a minimal module.exports pattern
    const sandbox: any = { module: { exports: {} }, exports: {}, console: { log: () => {}, warn: () => {}, error: () => {} } };
    vm.createContext(sandbox);
    const script = new vm.Script(code, { filename: filePath });
    script.runInContext(sandbox, { timeout: 2000 });
    const exported = sandbox.module.exports || sandbox.exports;
    // plugin can export default or module.exports
    const plugin = exported && (exported.default || exported) as any;
    if (!plugin || !plugin.id || !plugin.register) return null;
    return plugin as LinkBayPlugin;
  } catch (err) {
    console.error('plugin load error', filePath, err);
    return null;
  }
}

export async function loadAndRegisterPlugins() {
  // Ensure plugins dir exists and is not writable by untrusted users in prod
  try { fs.mkdirSync(PLUGINS_DIR, { recursive: true }); } catch (e) { /* ignore */ }

  const files = fs.readdirSync(PLUGINS_DIR).filter(f => f.endsWith('.js'));
  if (!files.length) return;

  // Load available plugins metadata into DB if missing (non-destructive)
  for (const f of files) {
    const full = path.join(PLUGINS_DIR, f);
    // attempt to use sandboxed worker
    let plugin = null as any;
    try {
      const sandbox = new PluginSandbox(full, f.replace(/\.js$/, ''));
      await sandbox.start();
      // ask worker to load and return plugin metadata
      const meta = await sandbox.register(null, {});
      if (meta && meta.result && meta.result.ok) {
        // fallback to loading metadata via vm to read id/name/version
        plugin = loadPluginFromFile(full);
      }
      sandbox.stop();
    } catch (err) {
      // fallback to vm load if sandbox failed
      plugin = loadPluginFromFile(full);
    }
    if (!plugin) continue;
    // upsert into available_plugins
    try {
      await knex('available_plugins').insert({ id: plugin.id, name: plugin.name, latest_version: plugin.version }).onConflict('id').merge({ name: plugin.name, latest_version: plugin.version });
    } catch (e) { console.warn('available_plugins upsert failed', e); }
    // read plugin manifest for version constraints and dependencies
    try {
      const manifestDir = path.join(PLUGINS_DIR, f.replace(/\.js$/, ''));
      const manifestPath = path.join(manifestDir, 'plugin-manifest.json');
      let manifest: any = null;
      if (fs.existsSync(manifestPath)) manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
      else {
        const pkgPath = path.join(manifestDir, 'package.json');
        if (fs.existsSync(pkgPath)) manifest = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
      }
      if (manifest) {
        try {
          await knex('available_plugins').where({ id: plugin.id }).update({ min_core_version: manifest.minCoreVersion || null, max_core_version: manifest.maxCoreVersion || null, dependencies: manifest.dependencies || null });
        } catch(e) { /* ignore */ }
        const okMin = satisfiesCore(manifest.minCoreVersion, CORE_VERSION);
        const okMax = manifest.maxCoreVersion ? satisfiesCore(manifest.maxCoreVersion, CORE_VERSION) : true;
        if (!okMin || !okMax) {
          try { await knex('tenant_plugins').where({ plugin_id: plugin.id }).update({ is_active: false }); console.warn('plugin disabled due core version mismatch', plugin.id); } catch(e) { }
        }
      }
    } catch (err) { /* ignore manifest errors */ }
  }

  // For each tenant that has active plugins, call register for each active plugin
  const activeRows = await knex('tenant_plugins').where({ is_active: true });
  for (const row of activeRows) {
    try {
      const pluginFile = files.find(f => f.includes(row.plugin_id));
      if (!pluginFile) continue;
      const fullPath = path.join(PLUGINS_DIR, pluginFile);
      // Check central approval status before registering for tenant
      try {
        const approvedRow = await knex('available_plugins').where({ id: row.plugin_id, is_approved: true }).first();
        if (!approvedRow) {
          console.warn(`plugin ${row.plugin_id} not approved in registry; skipping registration for tenant ${row.tenant_id}`);
          continue;
        }
      } catch (e) { console.warn('failed to check plugin approval', e); }
      // prefer sandboxed execution
      try {
        const sandbox = new PluginSandbox(fullPath, row.plugin_id);
        await sandbox.start();
        const ctx = { tenantId: row.tenant_id };
        await sandbox.start();
        await sandbox.register(row.tenant_id, ctx);
        // ask worker to register any declared routes/hooks; here we probe for routes
        try {
          await sandbox.registerHook('');
        } catch(e) {}
        // For plugin routes, register each route by delegating invocations to sandbox.callRoute
        // For simplicity we register a generic mount and assume plugin will expose routes by path
        registerPluginRoute(row.plugin_id, 'get', '/:route', async ({ method, path, req }) => {
          // delegate to sandbox and measure duration
          const start = Date.now();
          const r = await sandbox.callRoute(method, path, req);
          const duration = Date.now() - start;
          try {
            await knex('plugin_logs').insert({ plugin_id: row.plugin_id, tenant_id: row.tenant_id, level: 'info', message: 'route_invocation', meta: { method, path }, duration_ms: duration, created_at: new Date() });
          } catch(e){}
          // warn if slow
          const SLOW_MS = 500;
          if (duration > SLOW_MS) {
            try { await knex('plugin_logs').insert({ plugin_id: row.plugin_id, tenant_id: row.tenant_id, level: 'warn', message: 'route_slow', meta: { method, path, duration }, duration_ms: duration, created_at: new Date() }); } catch(e){}
            console.warn(`plugin route slow ${row.plugin_id} ${path} ${duration}ms`);
          }
          return r && r.result ? r.result : { status: 200, body: {} };
        });
        // register sandbox handler for product.created hook
        hookRegistry.registerSandboxHandler('product.created', row.plugin_id, sandbox, row.tenant_id);
        sandbox.stop();
        console.info(`Plugin ${row.plugin_id} sandbox-registered for tenant ${row.tenant_id}`);
      } catch (err) {
        // fallback to in-process VM execution
        const plugin = loadPluginFromFile(fullPath);
        if (!plugin) continue;
        const ctx = makeContext(plugin.id);
        // when plugin registers in-process, also hook into hookRegistry via local handler
        // plugins can call ctx.hooks.register inside register()
        // to ensure integration, make ctx.hooks.register call hookRegistry.registerLocal
        const originalRegister = ctx.hooks.register;
        ctx.hooks.register = (hook:any, handler:any) => {
          hookRegistry.registerLocal(hook, plugin.id, handler);
          originalRegister(hook, handler);
        };
        try { await plugin.register(ctx); console.info(`Plugin ${plugin.id} registered for tenant ${row.tenant_id}`); } catch(e) { console.error('register plugin failed', row.plugin_id, e); }
      }
    } catch (err) {
      console.error('register plugin failed', row.plugin_id, err);
    }
  }
}

export default { loadAndRegisterPlugins };
