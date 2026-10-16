<#
.SYNOPSIS
  Deploy or update the CV Studio module (cv_studio) on a Zakheni Odoo 18 instance.

.DESCRIPTION
  Fetches the J18Odoo repo, backs up the currently deployed cv_studio module, copies the
  module from the repo into custom-addons\cv_studio, ensures its Python dependencies are
  installed in the Odoo virtualenv, installs or upgrades the module in Odoo, restarts the
  server and verifies it answers HTTP.

  Safe by default: the existing deployed module is MOVED to custom-addons\backups\ before it
  is replaced, so a bad copy can be rolled back by moving it back.

.NOTES
  Requirements on the target machine:
    * Odoo 18 running from a venv (default C:\odoo18).
    * Microsoft Word installed (the engine uses Word COM to convert DOCX -> PDF).
    * Optional: an `opencode` executable for AI drafting (set later in
      CV Studio > Configuration > Settings).

.PARAMETER Install
  Force install (-i). By default the script upgrades (-u) an installed module and installs
  it automatically if it is not yet present.

.PARAMETER OpenCodeExe
  Full path to opencode.exe on this machine; written to the cv_studio.opencode_exe setting.

.PARAMETER SkipDeps
  Do not install the Python dependencies (python-docx, pymupdf, ...) into the venv.

.EXAMPLE
  .\deploy_cv_studio.ps1
.EXAMPLE
  .\deploy_cv_studio.ps1 -Install -OpenCodeExe "C:\opencode\opencode.exe"
.EXAMPLE
  .\deploy_cv_studio.ps1 -SourceDir "C:\Users\me\J18Odoo" -SkipPull
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
  [string]$ModuleName  = "cv_studio",
  [string]$RepoUrl     = "https://github.com/Zakheni/J18Odoo.git",
  [string]$Branch      = "master",
  [string]$SourceDir   = "",
  [string]$ServiceName = "Odoo18",
  [string]$OpenCodeExe = "",
  [switch]$SkipPull,
  [switch]$Install,
  [switch]$SkipDeps,
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
  if (-not (Test-Path (Join-Path $repo $ModuleName))) { Die "No $ModuleName folder in $repo" }
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

# --- 2. locate the module ---------------------------------------------------
$srcMod = Join-Path $repo $ModuleName
$manifest = Join-Path $srcMod "__manifest__.py"
if (-not (Test-Path $manifest)) { Die "No __manifest__.py in $srcMod" }
$ver = ((Select-String -Path $manifest -Pattern '"version"\s*:\s*"([^"]+)"').Matches[0].Groups[1].Value)
Step "Module $ModuleName version $ver"

# --- 3. python dependencies -------------------------------------------------
if (-not $SkipDeps) {
  Step "Ensuring venv dependencies (python-docx, pymupdf, openpyxl, pillow, pywin32)"
  & $VenvPython -m pip install --disable-pip-version-check --quiet python-docx pymupdf openpyxl pillow pywin32
  if ($LASTEXITCODE -ne 0) { Warn "pip install returned $LASTEXITCODE; continuing" } else { Ok "dependencies present" }
}

# --- 4. back up + copy ------------------------------------------------------
$target = Join-Path $AddonsDir $ModuleName
if (Test-Path $target) {
  $backupRoot = Join-Path $AddonsDir "backups"
  New-Item -ItemType Directory -Path $backupRoot -Force | Out-Null
  $bk = Join-Path $backupRoot ("{0}_{1}" -f $ModuleName, (Get-Date -Format "yyyyMMdd-HHmmss"))
  Move-Item $target $bk
  Ok "Backed up existing module -> $bk"
}
Step "Copying module -> $target"
robocopy $srcMod $target /E /XD __pycache__ /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { Die "robocopy failed (exit $LASTEXITCODE)" }
Ok "copied"

# --- 5. decide install vs upgrade ------------------------------------------
$pyState = Join-Path $env:TEMP "cvstd_statecheck.py"
@'
import sys, configparser, psycopg2
conf, db, mod = sys.argv[1], sys.argv[2], sys.argv[3]
c = configparser.ConfigParser(); c.read(conf)
o = c["options"] if c.has_section("options") else {}
try:
    conn = psycopg2.connect(host=o.get("db_host", "localhost"), port=o.get("db_port", "5432"),
                            dbname=db, user=o.get("db_user", "odoo"), password=o.get("db_password", ""))
    cur = conn.cursor()
    cur.execute("select state from ir_module_module where name=%s", (mod,))
    row = cur.fetchone()
    print(row[0] if row else "absent")
except Exception as e:
    print("unknown")
'@ | Set-Content -Path $pyState -Encoding UTF8
$state = (& $VenvPython $pyState $OdooConf $DbName $ModuleName 2>&1 | Select-Object -Last 1)
$isInstalled = ($state -eq "installed")
$flag = if ($Install -or -not $isInstalled) { "-i" } else { "-u" }
Step "DB state '$state' -> applying '$flag $ModuleName'"

# --- 6. stop / apply / start ------------------------------------------------
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

& $VenvPython $OdooBin -c $OdooConf -d $DbName $flag $ModuleName --stop-after-init --no-http
if ($LASTEXITCODE -ne 0) { Die "Module $flag failed (exit $LASTEXITCODE)" }
Ok "module applied"

# --- 7. optional setting ----------------------------------------------------
if ($OpenCodeExe) {
  Step "Setting cv_studio.opencode_exe = $OpenCodeExe"
  $pySet = Join-Path $env:TEMP "cvstd_setsetting.py"
  @'
import sys, configparser, psycopg2
conf, db, key, val = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
c = configparser.ConfigParser(); c.read(conf)
o = c["options"] if c.has_section("options") else {}
conn = psycopg2.connect(host=o.get("db_host", "localhost"), port=o.get("db_port", "5432"),
                        dbname=db, user=o.get("db_user", "odoo"), password=o.get("db_password", ""))
cur = conn.cursor()
cur.execute("select id from ir_config_parameter where key=%s", (key,))
row = cur.fetchone()
if row:
    cur.execute("update ir_config_parameter set value=%s where id=%s", (val, row[0]))
else:
    cur.execute("insert into ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date) "
                "values (%s, %s, 1, now(), 1, now())", (key, val))
conn.commit()
print("ok")
'@ | Set-Content -Path $pySet -Encoding UTF8
  & $VenvPython $pySet $OdooConf $DbName "cv_studio.opencode_exe" $OpenCodeExe | Out-Null
  Ok "setting written"
}

if (-not $NoRestart) {
  Step "Starting Odoo"
  if ($mode -eq "service") {
    Start-Service -Name $ServiceName
  } else {
    Start-Process -FilePath $VenvPython -ArgumentList @($OdooBin, "-c", $OdooConf, "-d", $DbName, "--http-port=$HttpPort", "--logfile=$LogFile") -WindowStyle Hidden
  }
}

# --- 8. verify --------------------------------------------------------------
Step "Waiting for http://localhost:$HttpPort/web/login"
$deadline = (Get-Date).AddSeconds(180)
$code = 0
do {
  Start-Sleep -Seconds 3
  try { $code = (Invoke-WebRequest -Uri "http://localhost:$HttpPort/web/login" -UseBasicParsing -TimeoutSec 5).StatusCode } catch { $code = 0 }
} until ($code -eq 200 -or (Get-Date) -gt $deadline)
if ($code -eq 200) { Ok "HTTP 200" } else { Warn "server did not answer 200 within 180s (check $LogFile)" }

$row = & $VenvPython $pyState $OdooConf $DbName $ModuleName 2>&1
Ok "DB state now: $row"

Write-Host ""
Write-Host "Done. Deployed $ModuleName $ver." -ForegroundColor Green
Write-Host "Rollback: move the newest folder in $AddonsDir\backups back to $target, then re-run with -NoRestart." -ForegroundColor DarkGray
