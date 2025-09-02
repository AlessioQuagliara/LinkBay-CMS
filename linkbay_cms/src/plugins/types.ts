export type PluginId = string;
export interface PluginLogger { debug(...args:any[]):void; info(...args:any[]):void; warn(...args:any[]):void; error(...args:any[]):void }
export interface LinkBayPlugin { id: PluginId; name: string; version: string; register(context: PluginContext): void | Promise<void>; }
export interface HookRegistrar { register<T=any>(hook: string, handler: (payload:T, meta:{ tenantId?: string | null })=>void|Promise<void>): void }
export interface PluginApiRouter { get(path:string, handler:any):void; post(path:string, handler:any):void; put(path:string, handler:any):void; delete(path:string, handler:any):void }
export interface AdminUiRegistrar { registerPanel(id:string, label:string, mountPath:string): void }
export interface EditorBlockRegistrar { registerBlock(def:{ id:string; name:string; schema?:any; renderPreview?: (data:any)=>string }): void }
export type PluginRequest = any;
export type PluginResponse = any;
export interface PluginContext { pluginId: PluginId; logger: PluginLogger; hooks: HookRegistrar; api: PluginApiRouter; admin: AdminUiRegistrar; editor?: EditorBlockRegistrar; settings: { get<T=any>(key:string):Promise<T|null>; set<T=any>(key:string, value:T):Promise<void> } }
