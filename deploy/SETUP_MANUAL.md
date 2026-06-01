# Zakheni Odoo 18 — Setup Manual

## Zakheni ICT (Pty) Ltd

---

## 1. Overview

This manual covers the installation and configuration of Odoo 18 Enterprise ERP with Zakheni ICT custom modules on a Windows Server. The system includes:

| Module | Purpose |
|--------|---------|
| **zakheni_config** | SARS-compliant company defaults (PAYE, UIF, SDL), ZAR currency, salary journal |
| **zakheni_helpdesk** | Per-customer helpdesk routing — tickets auto-assign to the customer's team |
| **zakheni_partner_enrich** | Enrich partner data (website, email, phone, address) via Google Custom Search |
| **zakheni_accounting** | Dashboard, dunning/follow-ups, cash flow forecast, multi-company consolidation, credit limits |
| **OCA modules** | Enhanced accounting (fiscal years, lock dates, deferrals, reconciliation, bank sync, DMS) |

---

## 2. System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows Server 2019 | Windows Server 2022 |
| RAM | 4 GB | 8 GB+ |
| CPU | 2 cores | 4+ cores |
| Disk | 20 GB free | 50 GB+ SSD |
| Database | PostgreSQL 16+ | PostgreSQL 17 |

---

## 3. Installation

### 3a. Quick Install with opencode

On the server, run opencode with the automated prompt:

```powershell
opencode -p "Execute ALL setup steps from https://raw.githubusercontent.com/Zakheni/J18Odoo/master/deploy/PROMPT_OPENCODE.md"
```

This will install PostgreSQL, Python, Git, clone Odoo 18 and all Zakheni modules, create the Python virtual environment, initialize the database, and register Odoo as a Windows service — fully automated.

### 3b. Manual Step-by-Step Install

#### Step 1: Install PostgreSQL 17

Download the installer from https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

Run the installer with these settings:
- **Installation directory**: `C:\Program Files\PostgreSQL\17`
- **Superuser password**: `openpgpwd`
- **Port**: `5432`
- **Locale**: default

After installation, create the Odoo database user:

```powershell
"C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -c "CREATE USER openpg WITH PASSWORD 'openpgpwd' CREATEDB SUPERUSER;"
"C:\Program Files\PostgreSQL\17\bin\psql" -U postgres -c "CREATE DATABASE odoo18 OWNER openpg;"
```

#### Step 2: Install Python 3.12

Download from https://www.python.org/downloads/

```powershell
python-3.12.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
```

#### Step 3: Install Git

```powershell
git-installer.exe /VERYSILENT /NORESTART /COMPONENTS=gitlfs
```

#### Step 4: Create Directory Structure

```powershell
$OdooDir = "C:\odoo18"
New-Item -ItemType Directory -Path $OdooDir, "$OdooDir\custom-addons", "$OdooDir\data" -Force
```

#### Step 5: Clone Odoo 18

```powershell
git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git C:\odoo18\server
```

#### Step 6: Clone Zakheni Modules

```powershell
git clone --depth 1 --branch master https://github.com/Zakheni/J18Odoo.git "$env:TEMP\J18Odoo"
Copy-Item "$env:TEMP\J18Odoo\*" "C:\odoo18\custom-addons" -Recurse -Force
Remove-Item "$env:TEMP\J18Odoo" -Recurse -Force
```

#### Step 7: Python Virtual Environment

```powershell
python -m venv C:\odoo18\venv
C:\odoo18\venv\Scripts\pip install --upgrade pip wheel setuptools
C:\odoo18\venv\Scripts\pip install -r C:\odoo18\server\requirements.txt
C:\odoo18\venv\Scripts\pip install google-api-python-client office365-rest-python-client
```

#### Step 8: Create odoo.conf

```powershell
$addonsPath = @()
$addonsPath += "C:\odoo18\server\odoo\addons"
Get-ChildItem "C:\odoo18\custom-addons" -Directory | Sort-Object Name | ForEach-Object { $addonsPath += $_.FullName }
$addonsPathStr = $addonsPath -join ","

@"
[options]
db_host = localhost
db_port = 5432
db_user = openpg
db_password = openpgpwd
db_name = odoo18
addons_path = $addonsPathStr
data_dir = C:\odoo18\data
admin_passwd = admin
list_db = True
workers = 2
max_cron_threads = 2
log_level = info
"@ | Out-File -FilePath "C:\odoo18\odoo.conf" -Encoding utf8
```

#### Step 9: Initialize Database

```powershell
C:\odoo18\venv\Scripts\python C:\odoo18\server\odoo-bin -c C:\odoo18\odoo.conf -d odoo18 -i base --without-demo=all --stop-after-init
```

#### Step 10: Install Custom Modules

```powershell
C:\odoo18\venv\Scripts\python C:\odoo18\server\odoo-bin -c C:\odoo18\odoo.conf -d odoo18 -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting --without-demo=all --stop-after-init
```

#### Step 11: Create Windows Service (using NSSM)

Download NSSM from https://nssm.cc/download:

```powershell
Invoke-WebRequest -Uri "https://github.com/nicedoc/nssm/releases/download/v2.24/nssm-2.24.zip" -OutFile "$env:TEMP\nssm.zip" -UseBasicParsing
Expand-Archive -Path "$env:TEMP\nssm.zip" -DestinationPath "$env:TEMP\nssm" -Force
Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" "C:\odoo18\nssm.exe"

# Create and start the service
C:\odoo18\nssm.exe install Odoo18 "C:\odoo18\venv\Scripts\python.exe" "C:\odoo18\server\odoo-bin -c C:\odoo18\odoo.conf"
C:\odoo18\nssm.exe set Odoo18 AppDirectory "C:\odoo18\server"
C:\odoo18\nssm.exe set Odoo18 DisplayName "Odoo 18 - Zakheni ICT"
C:\odoo18\nssm.exe set Odoo18 Start SERVICE_AUTO_START
C:\odoo18\nssm.exe set Odoo18 AppStdout "C:\odoo18\odoo.log"
C:\odoo18\nssm.exe set Odoo18 AppStderr "C:\odoo18\odoo-error.log"
C:\odoo18\nssm.exe start Odoo18
```

### 3c. Docker Deployment (Linux Server)

```bash
git clone https://github.com/Zakheni/J18Odoo.git
cd J18Odoo/deploy
cp .env.example .env
# Edit .env with your passwords
docker compose up -d
docker compose exec odoo odoo -d odoo18 -i base --stop-after-init
docker compose exec odoo odoo -d odoo18 -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting --stop-after-init
```

---

## 4. First Login

1. Open `http://localhost:8069` in a browser
2. Login with:
   - **Username**: `admin`
   - **Password**: `admin`
3. The system will prompt you to set up a new password on first login (recommended).

---

## 5. Post-Install Configuration

### 5a. Verify SARS/ZAR Settings

Navigate to **Settings → General Settings** and verify:
- **Company Name**: Zakheni ICT (Pty) Ltd
- **Currency**: ZAR (South African Rand)
- **SARS PAYE Number**: `7205614930`
- **SARS UIF Number**: `7205614930`
- **SARS SDL Number**: `S7205614930`
- **SARS Registration Number**: `7205614930`

These defaults are set automatically by `zakheni_config`. Update them if your actual SARS registration numbers differ.

### 5b. Configure Partner Enrichment

Go to **Settings → General Settings → Partner Enrich** and enter:
- **Google API Key** — from Google Cloud Console (enable Custom Search API)
- **Google Search Engine ID (cx)** — from https://programmablesearchengine.google.com/

Without these keys, the enrichment feature will not work.

### 5c. Configure Helpdesk Teams

Go to **Helpdesk → Teams** and create teams. Assign customers to teams via **Contacts → [Partner] → Edit → Helpdesk Team**.

### 5d. Configure Enterprise Accounting Settings

Go to **Settings → Enterprise Accounting** to configure:
- **Cash Flow Horizon** (default: 90 days)
- **Auto Follow-up Interval** (default: 7 days)

---

## 6. Module Architecture

```
J18Odoo/
├── deploy/                          # Deployment scripts & docs
│   ├── setup.ps1                    # Windows automated installer
│   ├── setup.bat                    # Double-click launcher
│   ├── Dockerfile                   # Odoo 18 Docker image
│   ├── docker-compose.yml           # Odoo + PostgreSQL services
│   ├── odoo.conf                    # Production config
│   ├── init.sh                      # First-run init script
│   ├── PROMPT_OPENCODE.md           # opencode automation prompt
│   ├── SETUP_MANUAL.md              # ← This document
│   └── USER_MANUAL.md               # End-user guide
│
├── zakheni_accounting/              # Enterprise accounting features
├── zakheni_config/                  # Company defaults & SARS setup
├── zakheni_helpdesk/                # Per-customer helpdesk routing
├── zakheni_partner_enrich/          # Google web enrichment
│
├── helpdesk/                        # OCA helpdesk_mgmt (16 submodules)
├── account-financial-tools/         # OCA accounting tools
├── account-invoicing/               # OCA invoicing
├── account-payment/                 # OCA payment
├── account-reconcile/               # OCA reconciliation
├── bank-statement-import/           # OCA bank import
├── dms/                             # OCA document management
├── payroll/                         # OCA payroll
├── l10n_za_hr_payroll/              # South African payroll
├── sharepoint_connector/            # SharePoint integration
└── ...other OCA repos
```

---

## 7. Daily Operations

### Starting / Stopping Odoo

```powershell
# Windows Service
nssm start Odoo18
nssm stop Odoo18
nssm restart Odoo18

# Docker
docker compose start
docker compose stop
docker compose restart
```

### Upgrading a Module

After making code changes to a custom module:

```powershell
C:\odoo18\venv\Scripts\python C:\odoo18\server\odoo-bin -c C:\odoo18\odoo.conf -d odoo18 -u zakheni_accounting --stop-after-init
```

For multiple modules:
```powershell
C:\odoo18\venv\Scripts\python C:\odoo18\server\odoo-bin -c C:\odoo18\odoo.conf -d odoo18 -u zakheni_accounting,zakheni_helpdesk --stop-after-init
```

### Checking Logs

```powershell
# Service logs
Get-Content C:\odoo18\odoo.log -Tail 50 -Wait

# Init/upgrade logs
Get-Content C:\odoo18\init.log -Tail 50
```

### Monitoring Cron Jobs

Go to **Settings → Technical → Scheduled Actions** to monitor:
- **Zakheni Accounting: Auto Follow-up** — sends dunning letters
- **Zakheni Accounting: Generate Cash Forecast** — updates cash flow projections

---

## 8. Backup & Restore

### PowerShell Backup Script

```powershell
$date = Get-Date -Format "yyyyMMdd_HHmmss"
$backupDir = "C:\odoo18\backups"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Database backup
& "C:\Program Files\PostgreSQL\17\bin\pg_dump" -U openpg -d odoo18 -F c -f "$backupDir\odoo18_$date.dump"

# Filestore backup
Compress-Archive -Path "C:\odoo18\data\filestore" -DestinationPath "$backupDir\filestore_$date.zip"

Write-Host "Backup saved to $backupDir"
```

### Docker Backup

```bash
cd /opt/odoo18/deploy
docker compose exec db pg_dump -U odoo18 odoo18 > backup_$(date +%Y%m%d).sql
docker compose exec odoo tar czf - /var/lib/odoo > filestore_$(date +%Y%m%d).tar.gz
```

### Restore

```powershell
# Database restore
& "C:\Program Files\PostgreSQL\17\bin\pg_restore" -U openpg -d odoo18 -c "C:\odoo18\backups\odoo18_20260101.dump"

# Filestore restore
Expand-Archive -Path "C:\odoo18\backups\filestore_20260101.zip" -DestinationPath "C:\odoo18\data" -Force

# Restart Odoo
nssm restart Odoo18
```

---

## 9. Troubleshooting

### Odoo won't start

**Check the log:**
```powershell
Get-Content C:\odoo18\odoo.log -Tail 30
```

**Common issues:**
| Symptom | Cause | Fix |
|---------|-------|-----|
| `Connection refused` | PostgreSQL not running | `net start postgresql_17` |
| `FATAL: password authentication failed` | Wrong DB password | Check `db_password` in `odoo.conf` |
| `Module not found` | Wrong addons_path | Verify path in odoo.conf |
| `Port 8069 already in use` | Another Odoo running | `nssm stop Odoo18` or change port |
| `address already in use` | Stale process | `taskkill /F /PID <pid>` |

### Module install fails

```powershell
# Check the full traceback
Get-Content C:\odoo18\init.log -Tail 100

# Common fixes:
# 1. Missing dependencies — install the dependent module first
# 2. Python package missing — pip install <package>
# 3. XML parse error — check view files for Odoo 18 syntax
```

### Python version issues

Odoo 18 requires Python 3.10–3.12. Python 3.13 is not yet supported.

```powershell
python --version
```

---

## 10. Security Checklist

- [ ] Change `admin_passwd` in `odoo.conf` from `admin` to a strong password
- [ ] Change PostgreSQL `openpg` password
- [ ] Place behind a reverse proxy (nginx) with HTTPS (Let's Encrypt)
- [ ] Set `proxy_mode = True` in `odoo.conf` when behind a proxy
- [ ] Set `list_db = False` in production to hide database list
- [ ] Restrict port 8069 to internal network only
- [ ] Enable Windows Firewall rules
- [ ] Schedule regular backups
- [ ] Enable Odoo logging to a dedicated log aggregator

---

## 11. Upgrading Odoo Version

```powershell
# Stop service
nssm stop Odoo18

# Backup
pg_dump -U openpg -d odoo18 > pre-upgrade.sql

# Pull new Odoo version
cd C:\odoo18\server
git fetch
git checkout origin/18.0 --force

# Update Python deps
C:\odoo18\venv\Scripts\pip install -r requirements.txt --upgrade

# Start and upgrade
nssm start Odoo18
```

---

*Document version 1.0 — Zakheni ICT (Pty) Ltd*
