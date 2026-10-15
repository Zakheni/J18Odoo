<#
.SYNOPSIS
  Deploy or update the Virtual Office module (virtual_office) on a Zakheni Odoo 18 instance.

.DESCRIPTION
  Fetches the J18Odoo repo, selects a dated build from virtual_office_builds\, backs up the
  currently deployed module, copies the build into custom-addons\virtual_office, upgrades the
  module in Odoo, restarts the server and verifies it answers HTTP.

  Safe by default: the existing deployed module is MOVED to custom-addons\backups\ before it is
  replaced, so a bad build can be rolled back by moving it back.

.PARAMETER Build
  Build folder to deploy (e.g. 2026-10-14_build4). Default: the newest build in the repo.

.PARAMETER SourceDir
  Use an existing J18Odoo checkout instead of cloning into %TEMP%.

.PARAMETER SkipPull
  Do not git pull an existing checkout.

.PARAMETER Install
  Install the module (-i) instead of upgrading it (-u). Use on a fresh database.

.PARAMETER NoRestart
  Upgrade/install the module but do not stop or start the Odoo server.

.EXAMPLE
  .\deploy_virtual_office.ps1
.EXAMPLE
  .\deploy_virtual_office.ps1 -Build 2026-10-14_build4
.EXAMPLE
  .\deploy_virtual_office.ps1 -SourceDir "C:\Users\me\J18Odoo" -SkipPull
.EXAMPLE
  .\deploy_virtual_office.ps1 -Install
#>
[CmdletBinding()]
param(
  [string]$OdooRoot    = "C:\odoo18",
  [string]$AddonsDir   = "",
  [string]$VenvPython  = "",
  [string]$OdooBin     = "",
  [string]$OdooConf    = "",
  [string]$DbName      = "odoo18",
  [int]   $HttpPort    = 8069,
  [string]$ModuleName  = "virtual_office",
  [string]$Build       = "",
  [string]$RepoUrl     = "https://github.com/Zakheni/J18Odoo.git",
  [string]$Branch      = "master",
  [string]$SourceDir   = "",
  [string]$ServiceName = "Odoo18",
  [switch]$SkipPull,
  [switch]$Install,
  [switch]$NoRestart
)

$ErrorActionPreference = "Stop"

function Step($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "    $m" -ForegroundColor Yellow }
function Die($m)  { Write-Host "ERROR: $m" -ForegroundColor Red; exit 1 }

# --- defaults ---------------------------------------------------------------
if (-not $AddonsDir)  { $AddonsDir  = Join-Path $OdooRoot "custom-addons" }
if (-not $VenvPython) { $VenvPython = Join-Path $OdooRoot "venv\Scripts\python.exe" }
if (-not $OdooBin)    { $OdooBin    = Join-Path $OdooRoot "server\odoo-bin" }
if (-not $OdooConf)   { $OdooConf   = Join-Path $OdooRoot "odoo.conf" }
$LogFile = Join-Path $OdooRoot "data\odoo.log"

foreach ($p in @($VenvPython, $OdooBin, $OdooConf)) {
  if (-not (Test-Path $p)) { Die "Not found: $p  (pass the right -OdooRoot or explicit paths)" }
}
if (-not (Test-Path $AddonsDir)) { New-Item -ItemType Directory -Path $AddonsDir -Force | Out-Null }

# --- 1. get the repo --------------------------------------------------------
Step "Resolving J18Odoo source"
if ($SourceDir) {
  $repo = $SourceDir
  if (-not (Test-Path (Join-Path $repo "virtual_office_builds"))) { Die "No virtual_office_builds in $repo" }
  if (-not $SkipPull -and (Test-Path (Join-Path $repo ".git"))) {
    git -C $repo pull --ff-only origin $Branch
    if ($LASTEXITCODE -ne 0) { Warn "git pull failed; using local checkout as-is" }
  }
} else {
  $repo = Join-Path $env:TEMP "J18Odoo_deploy"
  if (Test-Path (Join-Path $repo ".git")) {
    if (-not $SkipPull) {
      git -C $repo pull --ff-only origin $Branch
      if ($LASTEXITCODE -ne 0) { Warn "git pull failed; using cached checkout" }
    }
  } else {
    if (Test-Path $repo) { $repo = Join-Path $env:TEMP ("J18Odoo_deploy_" + (Get-Date -Format "yyyyMMddHHmmss")) }
    git clone --depth 1 --branch $Branch $RepoUrl $repo
    if ($LASTEXITCODE -ne 0) { Die "git clone failed" }
  }
}
Ok "repo: $repo"

# --- 2. pick the build ------------------------------------------------------
$buildsRoot = Join-Path $repo "virtual_office_builds"
if (-not (Test-Path $buildsRoot)) { Die "No virtual_office_builds in $repo" }
if ($Build) {
  $buildDir = Join-Path $buildsRoot $Build
  if (-not (Test-Path $buildDir)) {
    $avail = (Get-ChildItem $buildsRoot -Directory | Sort-Object Name | Select-Object -ExpandProperty Name) -join ", "
    Die "Build '$Build' not found. Available: $avail"
  }
} else {
  $buildDir = (Get-ChildItem $buildsRoot -Directory | Sort-Object Name | Select-Object -Last 1).FullName
}
$manifest = Join-Path $buildDir "__manifest__.py"
if (-not (Test-Path $manifest)) { Die "No __manifest__.py in $buildDir" }
$ver = ((Select-String -Path $manifest -Pattern '"version"\s*:\s*"([^"]+)"').Matches[0].Groups[1].Value)
Step "Selected build: $(Split-Path $buildDir -Leaf)  (module version $ver)"

# --- 3. back up + copy ------------------------------------------------------
$target = Join-Path $AddonsDir $ModuleName
if (Test-Path $target) {
  $backupRoot = Join-Path $AddonsDir "backups"
  New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
  $bk = Join-Path $backupRoot ("{0}_{1}" -f $ModuleName, (Get-Date -Format "yyyyMMdd-HHmmss"))
  Move-Item $target $bk
  Ok "Backed up existing module -> $bk"
}
Step "Copying build -> $target"
robocopy $buildDir $target /E /XD __pycache__ /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Die "robocopy failed (exit $LASTEXITCODE)" }
Ok "copied"

# --- 4. stop / upgrade / start ---------------------------------------------
$svc  = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
$mode = if ($svc) { "service" } else { "process" }

if (-not $NoRestart) {
  Step "Stopping Odoo ($mode)"
  if ($mode -eq "service") {
    if ($svc.Status -ne "Stopped") { Stop-Service -Name $ServiceName -Force; $svc.WaitForStatus("Stopped", "00:01:00") }
  } else {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
      Where-Object { $_.CommandLine -match "odoo-bin" } |
      ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
  }
  Start-Sleep -Seconds 2
}

$flag = if ($Install) { "-i" } else { "-u" }
Step "Applying module '$ModuleName' ($flag) in database '$DbName'"
& $VenvPython $OdooBin -c $OdooConf -d $DbName $flag $ModuleName --stop-after-init --no-http
if ($LASTEXITCODE -ne 0) { Die "Module $flag failed (exit $LASTEXITCODE)" }
Ok "module applied"

if (-not $NoRestart) {
  Step "Starting Odoo"
  if ($mode -eq "service") {
    Start-Service -Name $ServiceName
  } else {
    Start-Process -FilePath $VenvPython -ArgumentList @($OdooBin, "-c", $OdooConf, "-d", $DbName, "--http-port=$HttpPort", "--logfile=$LogFile") -WindowStyle Hidden
  }
}

# --- 5. verify --------------------------------------------------------------
Step "Waiting for http://localhost:$HttpPort/web/login"
$deadline = (Get-Date).AddSeconds(180)
$code = 0
do {
  Start-Sleep -Seconds 3
  try { $code = (Invoke-WebRequest -Uri "http://localhost:$HttpPort/web/login" -UseBasicParsing -TimeoutSec 5).StatusCode } catch { $code = 0 }
} until ($code -eq 200 -or (Get-Date) -gt $deadline)
if ($code -eq 200) { Ok "HTTP 200" } else { Warn "server did not answer 200 within 180s (check $LogFile)" }

# DB version check (best effort)
$pyCheck = Join-Path $env:TEMP "vo_vercheck.py"
@'
import sys, configparser, psycopg2
conf, db, mod = sys.argv[1], sys.argv[2], sys.argv[3]
c = configparser.ConfigParser(); c.read(conf)
o = c["options"] if c.has_section("options") else {}
conn = psycopg2.connect(host=o.get("db_host", "localhost"), port=o.get("db_port", "5432"),
                        dbname=db, user=o.get("db_user", "odoo"), password=o.get("db_password", ""))
cur = conn.cursor()
cur.execute("select latest_version, state from ir_module_module where name=%s", (mod,))
print(cur.fetchone())
'@ | Set-Content -Path $pyCheck -Encoding UTF8
try {
  $row = & $VenvPython $pyCheck $OdooConf $DbName $ModuleName 2>&1
  Ok "DB says: $row"
} catch { Warn "DB version check skipped: $_" }

Write-Host ""
Write-Host "Done. Deployed $ModuleName $ver from $(Split-Path $buildDir -Leaf)." -ForegroundColor Green
Write-Host "Rollback: move the newest folder in $AddonsDir\backups back to $target, then re-run with -NoRestart." -ForegroundColor DarkGray
