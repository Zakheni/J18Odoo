#!/usr/bin/env bash
set -euo pipefail

# ==============================================================
# Zakheni Odoo 18 — Bare-metal / VM Deployment Script
# Tested on Ubuntu 24.04 LTS
# ==============================================================

ODOO_VERSION="18.0"
ODOO_HOME="/opt/odoo18"
ODOO_USER="odoo"
POSTGRES_DB="odoo18"
POSTGRES_USER="odoo18"
POSTGRES_PASSWORD="$(openssl rand -base64 24)"
ADMIN_PASSWD="$(openssl rand -base64 12)"

REPO_URL="https://github.com/Zakheni/J18Odoo.git"
REPO_DIR="/tmp/J18Odoo"

echo "=== Zakheni Odoo 18 Server Setup ==="

# --- System dependencies ---
sudo apt-get update
sudo apt-get install -y \
  git python3 python3-pip python3-venv python3-dev \
  build-essential libxml2-dev libxslt1-dev libldap2-dev \
  libsasl2-dev libssl-dev libjpeg-dev libpq-dev \
  postgresql postgresql-contrib \
  wkhtmltopdf \
  curl wget

# --- Create odoo user ---
sudo useradd -m -d "$ODOO_HOME" -s /bin/bash "$ODOO_USER" 2>/dev/null || true

# --- PostgreSQL setup ---
sudo -u postgres psql -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD' CREATEDB;" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE $POSTGRES_DB OWNER $POSTGRES_USER;" 2>/dev/null || true
echo "Database: $POSTGRES_DB / User: $POSTGRES_USER / Password: $POSTGRES_PASSWORD"

# --- Clone repo ---
git clone --depth 1 --branch master "$REPO_URL" "$REPO_DIR"

# --- Clone Odoo 18 ---
git clone --depth 1 --branch "$ODOO_VERSION" https://github.com/odoo/odoo.git "$ODOO_HOME/server"

# --- Python venv ---
python3 -m venv "$ODOO_HOME/venv"
source "$ODOO_HOME/venv/bin/activate"
pip install --upgrade pip wheel setuptools
pip install -r "$ODOO_HOME/server/requirements.txt"
pip install google-api-python-client office365-rest-python-client

# --- Copy custom addons ---
mkdir -p "$ODOO_HOME/custom-addons"
cp -r "$REPO_DIR"/*/ "$ODOO_HOME/custom-addons/" 2>/dev/null || true

# --- Build addons_path ---
ADDONS_PATH="$ODOO_HOME/server/odoo/addons"
for dir in "$ODOO_HOME"/custom-addons/*/; do
  ADDONS_PATH="$ADDONS_PATH,$dir"
done

# --- Generate config ---
cat > "$ODOO_HOME/odoo.conf" << ODOOCONF
[options]
admin_passwd = $ADMIN_PASSWD
db_host = localhost
db_port = 5432
db_user = $POSTGRES_USER
db_password = $POSTGRES_PASSWORD
addons_path = $ADDONS_PATH
data_dir = $ODOO_HOME/data
log_level = info
workers = 4
max_cron_threads = 2
proxy_mode = False
ODOOCONF

# --- Systemd service ---
sudo tee /etc/systemd/system/odoo.service > /dev/null << SYSTEMD
[Unit]
Description=Odoo 18 - Zakheni ICT
After=network.target postgresql.service

[Service]
Type=simple
User=$ODOO_USER
Group=$ODOO_USER
ExecStart=$ODOO_HOME/venv/bin/python $ODOO_HOME/server/odoo-bin -c $ODOO_HOME/odoo.conf
WorkingDirectory=$ODOO_HOME/server
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SYSTEMD

# --- Permissions ---
sudo chown -R "$ODOO_USER:$ODOO_USER" "$ODOO_HOME"

# --- Enable & start ---
sudo systemctl daemon-reload
sudo systemctl enable odoo
sudo systemctl start odoo

# --- Cleanup ---
rm -rf "$REPO_DIR"

echo ""
echo "=== Setup Complete ==="
echo "Odoo:     http://$(curl -s ifconfig.me):8069"
echo "Database: $POSTGRES_DB"
echo "DB User:  $POSTGRES_USER"
echo "DB Pass:  $POSTGRES_PASSWORD"
echo "Admin:    admin / (set via admin_passwd in $ODOO_HOME/odoo.conf)"
echo ""
echo "Next: Install modules via Apps or run:"
echo "  sudo -u $ODOO_USER $ODOO_HOME/venv/bin/python $ODOO_HOME/server/odoo-bin \\"
echo "    -c $ODOO_HOME/odoo.conf -d $POSTGRES_DB \\"
echo "    -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting \\"
echo "    --stop-after-init"
