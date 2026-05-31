# Zakheni Odoo 18 Deployment

This directory contains a Docker-based deployment for Odoo 18 with Zakheni ICT custom modules.

## Prerequisites

- Docker & Docker Compose v2
- Git
- 4 GB+ RAM allocated to Docker

## Quick Start

```bash
# 1. Clone the repo (if not already done)
git clone https://github.com/Zakheni/J18Odoo.git
cd J18Odoo/deploy

# 2. Start services
docker compose up -d

# 3. Initialize database with all modules
docker compose exec odoo odoo -d odoo18 -i base --stop-after-init

# 4. Install custom modules
docker compose exec odoo odoo -d odoo18 \
  -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting \
  --stop-after-init

# 5. Open in browser
echo "Open http://localhost:8069"
```

## First Login

- URL: `http://<server-ip>:8069`
- Database: `odoo18`
- Admin password: `admin`
- Default user: `admin` / `admin`

## Production Setup

For production, change these in `docker-compose.yml` or `odoo.conf`:

- **Database password** — change `POSTGRES_PASSWORD` and `ODOO_DB_PASSWORD`
- **Admin password** — change `admin_passwd` in `odoo.conf`
- **Workers** — adjust `workers = 4` based on CPU cores (2 × cores + 1)
- **SSL** — place behind a reverse proxy (nginx/caddy) with Let's Encrypt

### Backup

```bash
docker compose exec db pg_dump -U odoo18 odoo18 > backup_$(date +%Y%m%d).sql
docker compose exec odoo tar czf - /var/lib/odoo > filestore_$(date +%Y%m%d).tar.gz
```

### Restore

```bash
docker compose exec -T db psql -U odoo18 -d odoo18 < backup_20250101.sql
docker compose exec odoo tar xzf - -C / < filestore_20250101.tar.gz
```

## Directory Layout

```
.
├── deploy/                    # ← Deployment files (this dir)
│   ├── docker-compose.yml     # Service definitions
│   ├── Dockerfile             # Odoo image with extra pip packages
│   ├── odoo.conf              # Production configuration
│   └── README.md
├── zakheni_accounting/        # Enterprise accounting (dashboard, dunning, etc.)
├── zakheni_config/            # Company defaults, SARS/ZAR setup
├── zakheni_helpdesk/          # Per-customer helpdesk routing
├── zakheni_partner_enrich/    # Google Custom Search partner enrichment
├── helpdesk/                  # OCA helpdesk_mgmt modules
├── account-financial-tools/   # OCA accounting tools
├── account-invoicing/         # OCA invoicing modules
├── ...
```

## Custom Modules

| Module | Description |
|--------|-------------|
| `zakheni_accounting` | Dashboard, Follow-ups, Cash Forecast, Consolidation, Credit Limit |
| `zakheni_config` | Company defaults (SARS PAYE/UIF/SDL), ZAR currency, salary journal |
| `zakheni_helpdesk` | Automatically routes tickets to customer's assigned team |
| `zakheni_partner_enrich` | Enriches partner data from Google Custom Search |

## Partner Enrichment Configuration

After login, go to **Settings → General Settings → Partner Enrich** and set:

- **Google API Key** — from Google Cloud Console
- **Google Search Engine ID (cx)** — from Programmable Search Engine

## Updating Modules

After code changes:

```bash
cd deploy
docker compose restart odoo   # picks up file changes from mounted volumes
docker compose exec odoo odoo -d odoo18 -u zakheni_accounting --stop-after-init
```
