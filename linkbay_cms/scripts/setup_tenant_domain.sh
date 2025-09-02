#!/usr/bin/env bash
set -euo pipefail

# Usage: sudo ./setup_tenant_domain.sh <tenant_id> <custom_domain> [app_port] [email_for_certbot]
TENANT_ID=${1:-}
DOMAIN=${2:-}
APP_PORT=${3:-3000}
CERTBOT_EMAIL=${4:-admin@yourplatform.com}

if [[ -z "$TENANT_ID" || -z "$DOMAIN" ]]; then
  echo "Usage: sudo $0 <tenant_id> <custom_domain> [app_port] [email_for_certbot]"
  exit 2
fi

if [[ "$EUID" -ne 0 ]]; then
  echo "This script must be run as root (or with sudo). Exiting." >&2
  exit 3
fi

SITES_AVAILABLE=/etc/nginx/sites-available
SITES_ENABLED=/etc/nginx/sites-enabled
CONF_PATH="$SITES_AVAILABLE/$DOMAIN"

echo "Generating nginx config for tenant $TENANT_ID -> $DOMAIN (proxy -> 127.0.0.1:$APP_PORT)"

cat > "$CONF_PATH" <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Proxy to local Node app
    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        # pass tenant id to the app
        proxy_set_header X-Tenant-Id $TENANT_ID;
    }

    client_max_body_size 50m;
}
EOF

ln -sf "$CONF_PATH" "$SITES_ENABLED/$DOMAIN"

echo "Testing nginx configuration..."
nginx -t

echo "Reloading nginx..."
if command -v systemctl >/dev/null 2>&1; then
  systemctl reload nginx
else
  service nginx reload
fi

echo "Requesting certificate via certbot for $DOMAIN (email: $CERTBOT_EMAIL)"
# certbot will edit the nginx config to add SSL block
certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$CERTBOT_EMAIL"

echo "Reloading nginx after certbot..."
if command -v systemctl >/dev/null 2>&1; then
  systemctl reload nginx
else
  service nginx reload
fi

echo "Done. $DOMAIN should be configured and have a Let's Encrypt certificate (if DNS points to this host)."
