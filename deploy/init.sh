#!/usr/bin/env bash
set -euo pipefail

echo "=== Zakheni Odoo 18 Initialization ==="

# Wait for Odoo to be ready
echo "Waiting for Odoo..."
until curl -s http://localhost:8069/web/login > /dev/null 2>&1; do
  sleep 2
done
echo "Odoo is up."

# Initialize database with base modules
echo "Initializing database..."
docker compose exec -T odoo odoo -d odoo18 -i base --stop-after-init

# Install our custom modules
echo "Installing Zakheni modules..."
docker compose exec -T odoo odoo -d odoo18 \
  -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting \
  --stop-after-init

echo "=== Done! Open http://localhost:8069 ==="
