import PluginSandbox from '../plugins/sandbox';

export enum HookName {
  PRODUCT_CREATED = 'product.created',
  ORDER_PROCESSING = 'order.processing',
  ADMIN_UI_EXTEND = 'admin.ui.extend'
}

type LocalHandler = { pluginId?: string; fn: (data:any, meta?:any)=>any|Promise<any> };
type SandboxHandler = { pluginId: string; tenantId?: number | string | null; sandbox: PluginSandbox };

class HookRegistry {
  private localHandlers: Map<string, LocalHandler[]> = new Map();
  private sandboxHandlers: Map<string, SandboxHandler[]> = new Map();

  registerLocal(hookName: string, pluginId: string | undefined, fn:(data:any, meta?:any)=>any|Promise<any>){
    const list = this.localHandlers.get(hookName) || [];
    list.push({ pluginId, fn });
    this.localHandlers.set(hookName, list);
  }

  registerSandboxHandler(hookName: string, pluginId: string, sandbox: PluginSandbox, tenantId?: number | string | null){
    const list = this.sandboxHandlers.get(hookName) || [];
    list.push({ pluginId, sandbox, tenantId });
    this.sandboxHandlers.set(hookName, list);
  }

  async callHook(hookName: string, data: any, meta?: any) {
    // run local handlers sequentially
    const local = this.localHandlers.get(hookName) || [];
    let current = data;
    for (const h of local) {
      try {
        const res = await Promise.resolve(h.fn(current, meta));
        // allow modification of data for processing hooks
        if (hookName === HookName.ORDER_PROCESSING && res !== undefined) current = res;
      } catch (e) {
        console.error('local hook error', h.pluginId, e);
      }
    }

    // run sandbox handlers (each may be tenant-scoped)
    const sand = this.sandboxHandlers.get(hookName) || [];
    for (const s of sand) {
      // if tenantId in meta and handler has tenantId filter, skip mismatches
      if (s.tenantId != null && meta && meta.tenantId != null && String(s.tenantId) !== String(meta.tenantId)) continue;
      try {
        const payload = { hook: hookName, data: current, meta };
        const resp = await s.sandbox.callHook(hookName, payload, meta);
        if (hookName === HookName.ORDER_PROCESSING && resp && resp.result && resp.result.modified) {
          current = resp.result.modified;
        }
      } catch (e) {
        console.error('sandbox hook error', s.pluginId, e);
      }
    }

    return current;
  }
}

const registry = new HookRegistry();
export default registry;
