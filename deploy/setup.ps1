param(
    [string]$OdooDir = "C:\odoo18",
    [string]$DbUser = "openpg",
    [string]$DbPassword = "openpgpwd",
    [string]$DbName = "odoo18",
    [string]$RepoUrl = "https://github.com/Zakheni/J18Odoo.git",
    [string]$OdooVersion = "18.0",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Step($msg) {
    Write-Host "`n>>> $msg" -ForegroundColor Cyan
}

function Test-Command($cmd) {
    try { Get-Command $cmd -ErrorAction Stop | Out-Null; return $true }
    catch { return $false }
}

# ==============================================================
# Admin check
# ==============================================================
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Relaunching as Administrator..." -ForegroundColor Yellow
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

Write-Host @"

  ╔══════════════════════════════════════════════╗
  ║     Zakheni Odoo 18 — Windows Setup         ║
  ╚══════════════════════════════════════════════╝

"@ -ForegroundColor Green

# ==============================================================
# 1. Prerequisites
# ==============================================================
Write-Step "Checking prerequisites..."

if (-not (Test-Command git)) {
    Write-Host "Installing Git..." -ForegroundColor Yellow
    $gitInstaller = "$env:TEMP\git-installer.exe"
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/Git-2.48.1-64-bit.exe" -OutFile $gitInstaller
    Start-Process $gitInstaller -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /RESTARTAPPLICATIONS /COMPONENTS=`"gitlfs`"" -Wait
    $env:Path += ";$env:ProgramFiles\Git\bin"
    [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:ProgramFiles\Git\bin", "User")
}

if (-not (Test-Command python)) {
    Write-Host "Installing Python 3.12..." -ForegroundColor Yellow
    $pyInstaller = "$env:TEMP\python-installer.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" -OutFile $pyInstaller
    Start-Process $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait
    refreshenv
}

if (-not (Test-Command psql)) {
    Write-Host "Installing PostgreSQL 17..." -ForegroundColor Yellow
    $pgInstaller = "$env:TEMP\postgresql-installer.exe"
    Invoke-WebRequest -Uri "https://get.enterprisedb.com/postgresql/postgresql-17.2-1-windows-x64.exe" -OutFile $pgInstaller
    Start-Process $pgInstaller -ArgumentList @(
        "--mode unattended"
        "--prefix `"$env:ProgramFiles\PostgreSQL\17`""
        "--datadir `"$env:ProgramFiles\PostgreSQL\17\data`""
        "--superpassword `"$DbPassword`""
        "--servicename `"postgresql_17`""
        "--serverport 5432"
    ) -Wait
    $env:Path += ";$env:ProgramFiles\PostgreSQL\17\bin"
    [Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "Machine") + ";$env:ProgramFiles\PostgreSQL\17\bin", "Machine")
}

Write-Host "  All prerequisites satisfied." -ForegroundColor Green

# ==============================================================
# 2. Node.js (for Odoo asset bundling)
# ==============================================================
if (-not (Test-Command node)) {
    Write-Step "Installing Node.js..."
    $nodeInstaller = "$env:TEMP\node-installer.msi"
    Invoke-WebRequest -Uri "https://nodejs.org/dist/v22.12.0/node-v22.12.0-x64.msi" -OutFile $nodeInstaller
    Start-Process msiexec -ArgumentList "/i `"$nodeInstaller`" /quiet /norestart" -Wait
}

# ==============================================================
# 3. Create directory structure
# ==============================================================
Write-Step "Setting up directory structure at $OdooDir..."

$serverDir = Join-Path $OdooDir "server"
$customDir = Join-Path $OdooDir "custom-addons"
$venvDir   = Join-Path $OdooDir "venv"

New-Item -ItemType Directory -Path $OdooDir -Force | Out-Null
New-Item -ItemType Directory -Path $customDir -Force | Out-Null

# ==============================================================
# 4. Clone Odoo 18
# ==============================================================
if (-not (Test-Path (Join-Path $serverDir "odoo-bin"))) {
    Write-Step "Cloning Odoo $OdooVersion..."
    git clone --depth 1 --branch $OdooVersion https://github.com/odoo/odoo.git $serverDir
} else {
    Write-Host "  Odoo source already exists, skipping clone." -ForegroundColor Yellow
}

# ==============================================================
# 5. Clone / update Zakheni custom modules
# ==============================================================
$repoDir = Join-Path $env:TEMP "J18Odoo"

if (Test-Path $repoDir) {
    Remove-Item -Path $repoDir -Recurse -Force
}

Write-Step "Cloning Zakheni modules from GitHub..."
git clone --depth 1 --branch master $RepoUrl $repoDir

# Copy only the directories we need (skip deploy/, .git/)
Get-ChildItem -Path $repoDir -Directory | ForEach-Object {
    $target = Join-Path $customDir $_.Name
    if ($_.Name -notin @('.git', 'deploy')) {
        if (Test-Path $target) {
            Remove-Item -Path $target -Recurse -Force
        }
        Copy-Item -Path $_.FullName -Destination $target -Recurse
    }
}

# Copy deployment files to OdooDir
$deployTarget = Join-Path $OdooDir "deploy"
if (Test-Path $deployTarget) { Remove-Item -Path $deployTarget -Recurse -Force }
Copy-Item -Path (Join-Path $repoDir "deploy") -Destination $deployTarget -Recurse

Remove-Item -Path $repoDir -Recurse -Force

Write-Host "  Custom modules deployed to $customDir" -ForegroundColor Green

# ==============================================================
# 6. Python virtual environment
# ==============================================================
Write-Step "Setting up Python virtual environment..."
if (-not (Test-Path (Join-Path $venvDir "Scripts\python.exe"))) {
    python -m venv $venvDir
} else {
    Write-Host "  Virtual env already exists." -ForegroundColor Yellow
}

$python = Join-Path $venvDir "Scripts\python.exe"
$pip = Join-Path $venvDir "Scripts\pip.exe"

Write-Step "Installing Python dependencies..."
& $pip install --upgrade pip wheel setuptools
& $pip install -r (Join-Path $serverDir "requirements.txt")
& $pip install google-api-python-client office365-rest-python-client

# ==============================================================
# 7. Build addons_path
# ==============================================================
Write-Step "Building addons path..."
$addonsPath = @()
$addonsPath += (Join-Path $serverDir "odoo" "addons")
Get-ChildItem -Path $customDir -Directory | Sort-Object Name | ForEach-Object {
    $addonsPath += $_.FullName
}
$addonsPathStr = $addonsPath -join ","

# ==============================================================
# 8. Create odoo.conf
# ==============================================================
Write-Step "Creating odoo.conf..."
$confPath = Join-Path $OdooDir "odoo.conf"
$dataDir = Join-Path $OdooDir "data"
New-Item -ItemType Directory -Path $dataDir -Force | Out-Null

@"
[options]
; Database
db_host = localhost
db_port = 5432
db_user = $DbUser
db_password = $DbPassword
db_name = $DbName
db_sslmode = prefer

; Addons
addons_path = $addonsPathStr

; Performance
workers = 2
max_cron_threads = 2
limit_memory_soft = 1073741824
limit_memory_hard = 2147483648
limit_time_cpu = 60
limit_time_real = 120

; Security
admin_passwd = admin
list_db = True
proxy_mode = False

; Data
data_dir = $dataDir

; Logging
log_level = info
log_handler = :WORKER,0,:WARNING,1
log_db = False

; Session
session_store = file
"@ | Out-File -FilePath $confPath -Encoding utf8

Write-Host "  Config written to $confPath" -ForegroundColor Green

# ==============================================================
# 9. Ensure PostgreSQL user and database
# ==============================================================
Write-Step "Configuring PostgreSQL..."
$psql = "psql -U postgres"
try {
    & cmd /c "echo CREATE USER $DbUser WITH PASSWORD '$DbPassword' CREATEDB; | $psql 2>nul"
    & cmd /c "echo CREATE DATABASE $DbName OWNER $DbUser; | $psql 2>nul"
    & cmd /c "echo ALTER USER $DbUser WITH SUPERUSER; | $psql 2>nul"
} catch {
    Write-Host "  PostgreSQL user/db may already exist (error is safe to ignore)." -ForegroundColor Yellow
}

# ==============================================================
# 10. Initialize database with all modules
# ==============================================================
Write-Step "Initializing database and installing modules..."
$initLog = Join-Path $OdooDir "init.log"
$odooBin = Join-Path $serverDir "odoo-bin"

& $python $odooBin -c $confPath -d $DbName -i base --without-demo=all --stop-after-init 2>&1 | Out-File -FilePath $initLog -Append
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Base init failed. Check $initLog" -ForegroundColor Red
    exit 1
}

Write-Step "Installing Zakheni custom modules..."
& $python $odooBin -c $confPath -d $DbName `
    -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting `
    --without-demo=all --stop-after-init 2>&1 | Out-File -FilePath $initLog -Append
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Module install failed. Check $initLog" -ForegroundColor Red
    exit 1
}

Write-Host "  Database initialized and modules installed!" -ForegroundColor Green

# ==============================================================
# 11. Install NSSM (Non-Sucking Service Manager) and create Windows service
# ==============================================================
Write-Step "Creating Windows service..."
$nssmPath = Join-Path $OdooDir "nssm.exe"
if (-not (Test-Path $nssmPath)) {
    $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $nssmZip = "$env:TEMP\nssm.zip"
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
    Expand-Archive -Path $nssmZip -DestinationPath "$env:TEMP\nssm" -Force
    Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" $nssmPath
    Remove-Item "$env:TEMP\nssm" -Recurse -Force
    Remove-Item $nssmZip -Force
}

# Stop existing service if any
& $nssmPath stop Odoo18 2>$null | Out-Null
& $nssmPath remove Odoo18 confirm 2>$null | Out-Null

# Create service
& $nssmPath install Odoo18 $python ($odooBin + " -c `"$confPath`"")
& $nssmPath set Odoo18 AppDirectory $serverDir
& $nssmPath set Odoo18 DisplayName "Odoo 18 — Zakheni ICT"
& $nssmPath set Odoo18 Description "Odoo 18 ERP with Zakheni ICT custom modules (Accounting, Helpdesk, Partner Enrich, SARS Payroll)"
& $nssmPath set Odoo18 Start SERVICE_AUTO_START
& $nssmPath set Odoo18 AppStdout (Join-Path $OdooDir "odoo.log")
& $nssmPath set Odoo18 AppStderr (Join-Path $OdooDir "odoo-error.log")
& $nssmPath set Odoo18 AppRotateFiles 1
& $nssmPath set Odoo18 AppRotateOnline 1
& $nssmPath set Odoo18 AppRotateSeconds 86400
& $nssmPath set Odoo18 AppRotateBytes 10485760

# Start service
& $nssmPath start Odoo18

Write-Host "  Odoo 18 service created and started!" -ForegroundColor Green

# ==============================================================
# 12. Create convenient desktop shortcut
# ==============================================================
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "Odoo 18 (Zakheni).url"
@"
[InternetShortcut]
URL=http://localhost:8069
"@ | Out-File -FilePath $shortcutPath -Encoding ascii

# ==============================================================
# Summary
# ==============================================================
Write-Host @"

  ╔══════════════════════════════════════════════╗
  ║              Setup Complete!                  ║
  ╠══════════════════════════════════════════════╣
  ║  Odoo:     http://localhost:8069             ║
  ║  DB:       $DbName                          ║
  ║  DB User:  $DbUser                           ║
  ║  DB Pass:  $DbPassword                       ║
  ║  Login:    admin / admin                     ║
  ║  Service:  Odoo18 (automatic startup)        ║
  ║  Config:   $confPath          ║
  ║  Logs:     $OdooDir\odoo.log      ║
  ╚══════════════════════════════════════════════╝

  Installed modules:
    - zakheni_config (SARS/ZAR defaults)
    - zakheni_helpdesk (per-customer ticket routing)
    - zakheni_partner_enrich (Google web enrichment)
    - zakheni_accounting (dashboard, dunning, cash flow, consolidation)

  Commands:
    Restart:  nssm restart Odoo18
    Stop:     nssm stop Odoo18
    Upgrade:  python odoo-bin -c odoo.conf -d odoo18 -u zakheni_accounting

"@ -ForegroundColor Green

Start-Process "http://localhost:8069"
