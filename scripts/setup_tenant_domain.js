#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

if (process.argv.length < 4) {
  console.error('Usage: node setup_tenant_domain.js <tenant_id> <custom_domain> [app_port] [email]');
  process.exit(2);
}

const tenantId = process.argv[2];
const domain = process.argv[3];
const appPort = process.argv[4] || '3000';
const email = process.argv[5] || 'admin@yourplatform.com';

const sitesAvailable = '/etc/nginx/sites-available';
const sitesEnabled = '/etc/nginx/sites-enabled';
const confPath = path.join(sitesAvailable, domain);

const config = `server {
  listen 80;
  server_name ${domain};

  location / {
    proxy_pass http://127.0.0.1:${appPort};
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Tenant-Id ${tenantId};
  }
}
`;

fs.writeFileSync(confPath, config, { mode: 0o644 });
try {
  execSync(`ln -sf ${confPath} ${path.join(sitesEnabled, domain)}`);
  execSync('nginx -t', { stdio: 'inherit' });
  execSync('systemctl reload nginx || service nginx reload', { stdio: 'inherit' });
  execSync(`certbot --nginx -d ${domain} --non-interactive --agree-tos -m ${email}`, { stdio: 'inherit' });
  execSync('systemctl reload nginx || service nginx reload', { stdio: 'inherit' });
  console.log('Done: domain configured');
} catch (err) {
  console.error('Error:', err.message);
  process.exit(1);
}
