"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.registerPluginRoute = registerPluginRoute;
const express_1 = __importDefault(require("express"));
const router = express_1.default.Router();
function safePath(pathStr) {
    if (!pathStr.startsWith('/'))
        pathStr = '/' + pathStr;
    if (pathStr.includes('..'))
        throw new Error('invalid path');
    // only allow basic chars
    if (!/^\/[a-zA-Z0-9_\-\/]*$/.test(pathStr))
        throw new Error('invalid path characters');
    return pathStr;
}
function registerPluginRoute(pluginId, method, pluginPath, invoker) {
    const m = method.toLowerCase();
    const safe = safePath(pluginPath);
    const mountPath = '/' + encodeURIComponent(pluginId) + safe; // router is mounted at /api/plugin
    const handler = async (req, res) => {
        try {
            const minimalReq = {
                params: req.params || {},
                query: req.query || {},
                body: req.body,
                headers: req.headers || {},
                tenantId: req.tenantId || null,
                userId: req.userId || null
            };
            const result = await invoker({ method: m, path: pluginPath, req: minimalReq });
            if (result && result.headers)
                Object.entries(result.headers).forEach(([k, v]) => res.setHeader(k, String(v)));
            res.status(result && result.status ? result.status : 200).json(result && result.body !== undefined ? result.body : {});
        }
        catch (err) {
            console.error('plugin route error', pluginId, err);
            res.status(500).json({ error: 'plugin_error' });
        }
    };
    // remove existing route if any to avoid duplicates
    try {
        // express doesn't provide a simple remove; we allow multiple registrations but prefer idempotent
    }
    catch (e) { }
    router[m](mountPath, handler);
    console.info(`mounted plugin route [${method.toUpperCase()}] /api/plugin${mountPath}`);
}
exports.default = router;
