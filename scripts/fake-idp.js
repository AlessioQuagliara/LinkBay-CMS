const http = require('http');
const url = require('url');
const zlib = require('zlib');

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);
  if (parsed.pathname !== '/sso') {
    res.writeHead(404, {'Content-Type':'text/plain'});
    res.end('Not found');
    return;
  }
  const saml = parsed.query.SAMLRequest || parsed.query.SAMLResponse || parsed.query.SAML || '';
  let decoded = null;
  try {
    const raw = String(saml);
    const buf = Buffer.from(raw, 'base64');
    // try inflateRaw (common for SAMLRequest)
    try {
      const inflated = zlib.inflateRawSync(buf).toString('utf8');
      decoded = inflated;
    } catch (e) {
      // fallback: treat as plain base64 xml
      decoded = buf.toString('utf8');
    }
  } catch (e) {
    decoded = null;
  }
  res.writeHead(200, {'Content-Type':'text/html; charset=utf-8'});
  res.write('<html><body>');
  res.write('<h2>Fake IdP /sso</h2>');
  res.write('<p>Raw SAML param (first 200 chars):</p><pre>' + String(saml).slice(0,200) + '</pre>');
  if (decoded) {
    res.write('<p>Decoded SAML (first 2000 chars):</p><pre>' + decoded.replace(/</g,'&lt;').slice(0,2000) + '</pre>');
  } else {
    res.write('<p>Unable to decode SAMLRequest.</p>');
  }
  res.write('<p><a href="/">OK</a></p>');
  res.end('</body></html>');
});

const PORT = process.env.FAKE_IDP_PORT || 9080;
server.listen(Number(PORT), '127.0.0.1', () => {
  console.log('Fake IdP listening on http://127.0.0.1:' + PORT);
});
