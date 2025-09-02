/**
 * LinkBay CMS Plugin SDK
 * This package exports the minimal, strict types and interfaces that a plugin
 * may implement to interact with the LinkBay core. The runtime will only
 * expose the approved surfaces from PluginContext, never raw Express/DB.
 */

export type PluginId = string;

export interface LinkBayPlugin {
  id: PluginId;
  name: string;
  version: string;
  /**
   * Called once when the plugin is registered. Must be synchronous or return a Promise<void>.
   * The context exposes only approved APIs (hooks, api, admin, logger).
   */
  register(context: PluginContext): void | Promise<void>;
}

/** Allowed extension points - whitelist only these */
export enum ExtensionPoint {
  HOOKS = 'hooks',
  API_ROUTES = 'api_routes',
  ADMIN_UI = 'admin_ui',
  EDITOR_BLOCKS = 'editor_blocks'
}

/** Hook types that core exposes. Plugins can register handlers for those hooks. */
export enum CoreHook {
  PAGE_RENDER = 'page.render',
  PRODUCT_SAVE = 'product.save',
  ORDER_PLACED = 'order.placed'
}

/** Strongly-typed logger interface provided to plugins */
export interface PluginLogger {
  debug(...args: any[]): void;
  info(...args: any[]): void;
  warn(...args: any[]): void;
  error(...args: any[]): void;
}

/** Limited router surface - only allows registering route handlers under a safe prefix. */
export interface PluginApiRouter {
  /**
   * Register a GET route under /_plugins/:pluginId/* to avoid collisions.
   * handler receives a minimal request/response subset.
   */
  get(path: string, handler: PluginRequestHandler): void;
  post(path: string, handler: PluginRequestHandler): void;
  put(path: string, handler: PluginRequestHandler): void;
  delete(path: string, handler: PluginRequestHandler): void;
}

/** Minimal request/response types exposed to plugins - no access to raw Express objects */
export type PluginRequest = {
  params: Record<string, string>;
  query: Record<string, string | undefined>;
  body?: any;
  headers: Record<string, string | undefined>;
  tenantId?: string | null;
  userId?: string | null;
};

export type PluginResponse = {
  status(code: number): PluginResponse;
  json(obj: any): void;
  send(body: string): void;
};

export type PluginRequestHandler = (req: PluginRequest, res: PluginResponse) => Promise<void> | void;

/** Hook registration API - typed and scoped */
export interface HookRegistrar {
  /** Register a handler for a core hook. Handler is synchronous or async. */
  register<T = any>(hook: CoreHook, handler: (payload: T, meta: { tenantId?: string | null }) => void | Promise<void>): void;
}

/** Admin UI surface - plugins can register a riser to render a specific admin panel.
 * The core will render the panel in an iframe or a restricted container; the plugin
 * should provide a relative URL under the safe /_plugins/:id/admin path.
 */
export interface AdminUiRegistrar {
  registerPanel(id: string, label: string, mountPath: string): void;
}

/** Editor block registration API - allow plugins to register blocks for the editor. */
export interface EditorBlockRegistrar {
  registerBlock(def: { id: string; name: string; schema?: any; renderPreview?: (data: any) => string }): void;
}

/** The PluginContext passed into register(). Only approved surfaces are included. */
export interface PluginContext {
  readonly pluginId: PluginId;
  readonly logger: PluginLogger;
  readonly hooks: HookRegistrar;
  readonly api: PluginApiRouter;
  readonly admin: AdminUiRegistrar;
  readonly editor?: EditorBlockRegistrar;
  /** A tiny key/value store for plugin-scoped settings (persisted by core). */
  settings: {
    get<T = any>(key: string): Promise<T | null>;
    set<T = any>(key: string, value: T): Promise<void>;
  };
}

export default {} as {
  LinkBayPlugin: LinkBayPlugin;
};
