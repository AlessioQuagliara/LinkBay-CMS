LinkBay CMS Plugin SDK
======================

This package exports a small, strict TypeScript surface for writing LinkBay CMS plugins. The
goal is to provide controlled extensibility: plugins get only approved APIs. The runtime will
never hand raw Express or DB instances to plugins.

Main concepts
-------------
- `LinkBayPlugin` - plugin entry contract (id, name, version, register(context))
- `PluginContext` - limited API surface: `hooks`, `api`, `admin`, `editor?`, `logger`, `settings`
- `ExtensionPoint` - enumerates allowed extension points.

Security model
--------------
- Plugins operate in a sandboxed manner: request/response objects are minimal and lack direct
  access to DB credentials or Express internals.
- API routes registered by plugins are mounted under safe prefixes (`/_plugins/:id/...`) and
  subject to rate limits and auth enforced by the core.
- Hooks run with controlled payloads; plugins should not be able to mutate core state directly.

Usage
-----
Create a package that depends on `@linkbaycms/plugin-sdk` and export a default object implementing
`LinkBayPlugin`.

Example
-------
```ts
import { LinkBayPlugin } from '@linkbaycms/plugin-sdk';

const plugin: LinkBayPlugin = {
  id: 'acme.hello',
  name: 'Acme Hello',
  version: '0.1.0',
  async register(ctx) {
    ctx.hooks.register('page.render', async (payload) => {
      ctx.logger.info('page.render', payload);
    });
    ctx.api.get('/hello', (req, res) => res.json({ hello: 'world' }));
  }
};

export default plugin;
```
