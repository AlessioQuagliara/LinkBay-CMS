#!/bin/bash
set -e

# Variabili di configurazione
PROJECT_DIR="/var/www/CMS_DEF"
VENV_DIR="$PROJECT_DIR/venv"
LOG_DIR="$PROJECT_DIR/logs"
UWSGI_CMS_INI="$PROJECT_DIR/uwsgi_cms.ini"
UWSGI_LANDING_INI="$PROJECT_DIR/uwsgi_landing.ini"
SYSTEMD_CMS_SERVICE="/etc/systemd/system/uwsgi-cms.service"
SYSTEMD_LANDING_SERVICE="/etc/systemd/system/uwsgi-landing.service"
NGINX_CMS_CONF="/etc/nginx/sites-available/linkbay-cms"
NGINX_LANDING_CONF="/etc/nginx/sites-available/linkbay-cms-landing"

echo "==> Creazione della directory dei log (se non esiste)"
mkdir -p "$LOG_DIR"
chown www-data:www-data "$LOG_DIR"

echo "==> Creazione del file uwsgi_cms.ini per il CMS (porta 5001)"
cat <<EOF > "$UWSGI_CMS_INI"
[uwsgi]
# Specifica il modulo e l'applicazione Flask
module = app:app

# Imposta la directory di lavoro
chdir = $PROJECT_DIR

# Abilita il processo master e definisci il numero di worker
master = true
processes = 4

# Specifica il binding: HTTP su 127.0.0.1:5001
http = 127.0.0.1:5001

# Pulizia dei file temporanei al termine
vacuum = true

# Arresto ordinato dei worker
die-on-term = true

# Logging (opzionale)
logto = $LOG_DIR/uwsgi_cms.log
EOF

echo "==> Creazione del file uwsgi_landing.ini per la Landing App (porta 5000)"
cat <<EOF > "$UWSGI_LANDING_INI"
[uwsgi]
# Specifica il modulo e l'applicazione Flask per la landing
module = landing_app:app

# Imposta la directory di lavoro
chdir = $PROJECT_DIR

master = true
processes = 4

# Binding su porta 5000
http = 127.0.0.1:5000

vacuum = true
die-on-term = true

# Logging per la Landing App
logto = $LOG_DIR/uwsgi_landing.log
EOF

echo "==> Creazione del file systemd per uwsgi-cms.service"
cat <<EOF > "$SYSTEMD_CMS_SERVICE"
[Unit]
Description=uWSGI instance for CMS (app.py)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uwsgi --ini $UWSGI_CMS_INI
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "==> Creazione del file systemd per uwsgi-landing.service"
cat <<EOF > "$SYSTEMD_LANDING_SERVICE"
[Unit]
Description=uWSGI instance for Landing App (landing_app.py)
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uwsgi --ini $UWSGI_LANDING_INI
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "==> Ricarico il daemon di systemd"
systemctl daemon-reload

echo "==> Abilito e avvio il servizio uwsgi-cms.service"
systemctl enable uwsgi-cms.service
systemctl start uwsgi-cms.service

echo "==> Abilito e avvio il servizio uwsgi-landing.service"
systemctl enable uwsgi-landing.service
systemctl start uwsgi-landing.service

echo "==> Creazione della configurazione Nginx per il CMS"
cat <<EOF > "$NGINX_CMS_CONF"
server {
    listen 80;
    server_name www.linkbay-cms.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "==> Creazione della configurazione Nginx per la Landing App (wildcard)"
cat <<EOF > "$NGINX_LANDING_CONF"
server {
    listen 80;
    server_name *.yoursite-linkbay-cms.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "==> Abilitazione delle configurazioni Nginx"
ln -sf "$NGINX_CMS_CONF" /etc/nginx/sites-enabled/
ln -sf "$NGINX_LANDING_CONF" /etc/nginx/sites-enabled/

echo "==> Test della configurazione Nginx"
nginx -t

echo "==> Ricarico Nginx"
systemctl reload nginx

echo "==> Configurazione completata."
echo "Verifica lo stato dei servizi:"
systemctl status uwsgi-cms.service --no-pager
systemctl status uwsgi-landing.service --no-pager