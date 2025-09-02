"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const router = (0, express_1.Router)();
// POST /api/editor/preview
// Accepts JSON { html, css, components } and returns a full HTML page
// This endpoint does NOT persist data and sets no-store cache headers.
router.post('/preview', async (req, res) => {
    try {
        const { html = '', css = '', components = null } = req.body || {};
        // basic sanitization - ensure strings
        const safeHtml = typeof html === 'string' ? html : '';
        const safeCss = typeof css === 'string' ? css : '';
        // Build a minimal HTML page for preview. Include common site assets so preview resembles production.
        const preview = `<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>Preview</title>
    <!-- Common site CSS (may be overridden by tenant CSS) -->
    <link rel="stylesheet" href="/static/css/main.css" />
    <!-- Inline editor CSS -->
    <style>${safeCss}</style>
  </head>
  <body>
    ${safeHtml}
    <!-- Common site JS -->
    <script src="/static/js/app.js"></script>
  </body>
</html>`;
        // Prevent caching of preview responses
        res.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
        res.set('Pragma', 'no-cache');
        res.set('Expires', '0');
        res.set('Surrogate-Control', 'no-store');
        // Return as HTML
        res.type('html').send(preview);
    }
    catch (err) {
        res.status(500).json({ error: 'preview_error', detail: String(err) });
    }
});
exports.default = router;
