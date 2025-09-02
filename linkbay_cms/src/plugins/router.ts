import express from 'express';
const router = express.Router();

type Invoker = (opts: { method: string; path: string; req: any }) => Promise<{ status?: number; headers?: any; body?: any }>;

function safePath(pathStr: string) {
  if (!pathStr.startsWith('/')) pathStr = '/' + pathStr;
  if (pathStr.includes('..')) throw new Error('invalid path');
  // only allow basic chars
  if (!/^\/[a-zA-Z0-9_\-\/]*$/.test(pathStr)) throw new Error('invalid path characters');
  return pathStr;
}

export function registerPluginRoute(pluginId: string, method: string, pluginPath: string, invoker: Invoker) {
  const m = method.toLowerCase();
  const safe = safePath(pluginPath);
  const mountPath = '/' + encodeURIComponent(pluginId) + safe; // router is mounted at /api/plugin

  const handler = async (req: any, res: any) => {
    try {
      const minimalReq = {
        params: req.params || {},
        query: req.query || {},
        body: req.body,
        headers: req.headers || {},
        tenantId: (req as any).tenantId || null,
        userId: (req as any).userId || null
      };
      const result = await invoker({ method: m, path: pluginPath, req: minimalReq });
      if (result && result.headers) Object.entries(result.headers).forEach(([k,v])=>res.setHeader(k, String(v)));
      res.status(result && result.status ? result.status : 200).json(result && result.body !== undefined ? result.body : {});
    } catch (err:any) {
      console.error('plugin route error', pluginId, err);
      res.status(500).json({ error: 'plugin_error' });
    }
  };

  // remove existing route if any to avoid duplicates
  try {
    // express doesn't provide a simple remove; we allow multiple registrations but prefer idempotent
  } catch (e) {}

  (router as any)[m](mountPath, handler);
  console.info(`mounted plugin route [${method.toUpperCase()}] /api/plugin${mountPath}`);
}

export default router;
