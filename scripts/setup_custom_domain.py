#!/usr/bin/env python3
import os
import sys
import subprocess

NGINX_AVAILABLE = "/etc/nginx/sites-available"
NGINX_ENABLED = "/etc/nginx/sites-enabled"
UWSGI_SOCKET_PATH = "/run/uwsgi/linkbaycms.sock"
LOG_PATH = "/var/www/CMS_DEF/logs/uwsgi_cms.log"
TEMPLATE_PATH = "/var/www/CMS_DEF/scripts/nginx_template.conf"

def create_nginx_config(domain):
    config = f"""
server {{
    server_name {domain} www.{domain};

    location / {{
        include uwsgi_params;
        uwsgi_pass unix:{UWSGI_SOCKET_PATH};
    }}

    access_log {LOG_PATH};
    error_log {LOG_PATH};

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/{domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{domain}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}}

server {{
    if ($host = www.{domain}) {{
        return 301 https://$host$request_uri;
    }}

    listen 80;
    server_name {domain} www.{domain};
    return 404;
}}
""".strip()

    config_path = os.path.join(NGINX_AVAILABLE, domain)
    with open(config_path, 'w') as f:
        f.write(config)

    print(f"✅ File Nginx creato: {config_path}")

def enable_nginx_config(domain):
    src = os.path.join(NGINX_AVAILABLE, domain)
    dest = os.path.join(NGINX_ENABLED, domain)
    if not os.path.exists(dest):
        os.symlink(src, dest)
        print(f"🔗 Symlink creato: {dest}")
    else:
        print("⚠️ Symlink già esistente")

def obtain_ssl(domain):
    try:
        subprocess.run(["certbot", "--nginx", "-d", domain, "-d", f"www.{domain}"], check=True)
        print("🔐 Certificato SSL rilasciato con successo")
    except subprocess.CalledProcessError:
        print("❌ Errore durante il rilascio del certificato")

def reload_nginx():
    subprocess.run(["systemctl", "reload", "nginx"])
    print("♻️ Nginx ricaricato")

def main():
    if len(sys.argv) < 2:
        print("❌ Specificare il dominio. Uso: python3 setup_custom_domain.py dominio.com")
        return

    domain = sys.argv[1].strip().lower()
    print(f"🚀 Inizio setup dominio personalizzato: {domain}")

    create_nginx_config(domain)
    enable_nginx_config(domain)
    reload_nginx()
    obtain_ssl(domain)
    reload_nginx()

    print(f"✅ Dominio {domain} configurato con successo!")

if __name__ == "__main__":
    main()