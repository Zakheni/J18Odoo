<#
.SYNOPSIS
  Diagnose and fix "The request sent to the server was too large" (HTTP 413) on a
  Windows Odoo 18 server (CV Studio pack uploads).

.DESCRIPTION
  Odoo's web client shows that message for any HTTP 413 response. A 413 can come from:
    * a reverse proxy in front of Odoo  (nginx / IIS / Apache), or
    * Odoo itself (hard-coded 128 MiB body cap).
  This script detects which is in play, raises the body limit (with a backup of the
  file it edits), and then probes the server with a large POST to confirm the new
  ceiling. It changes nothing unless it finds a proxy it can safely patch.

  Safe: every config file is copied to a timestamped backup before editing; nothing
  is deleted. Use -NoApply to only report.

.PARAMETER NewLimitMB
  Body limit to set on the proxy, in megabytes (default 200).

.PARAMETER TestMB
  Size of the verification POST, in MB (default: NewLimitMB, capped at 150).

.PARAMETER TestUrl
  URL to probe. Default: http://localhost:<odoo port>/web/login.
  For a proxied server, pass the public URL, e.g. http://odoo.zakheni.local/.

.EXAMPLE
  .\fix_cv_studio_upload_limit.ps1
.EXAMPLE
  .\fix_cv_studio_upload_limit.ps1 -NoApply
.EXAMPLE
  .\fix_cv_studio_upload_limit.ps1 -TestUrl "http://odoo.zakheni.local/" -NewLimitMB 300
#>
[CmdletBinding()]
param(
  [string]$OdooRoot   = "C:\odoo18",
  [string]$OdooConf   = "",
  [int]   $OdooPort   = 0,
  [int]   $NewLimitMB = 200,
  [int]   $TestMB     = 0,
  [string]$TestUrl    = "",
  [string]$ServiceName = "Odoo18",
  [switch]$NoApply,
  [switch]$SkipVerify
)

$ErrorActionPreference = "Stop"
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$BackupDir = Join-Path $env:TEMP "cvstudio_limit_backup_$stamp"
New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null

function Step($m) { Write-Host "==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "    $m" -ForegroundColor Green }
function Warn($m) { Write-Host "    $m" -ForegroundColor Yellow }
function Info($m) { Write-Host "    $m" -ForegroundColor Gray }

$limitBytes = $NewLimitMB * 1MB

# --- resolve Odoo port ------------------------------------------------------
if (-not $OdooConf) { $OdooConf = Join-Path $OdooRoot "odoo.conf" }
if ($OdooPort -eq 0) {
  if (Test-Path $OdooConf) {
    $m = Select-String -Path $OdooConf -Pattern '^\s*http_port\s*=\s*(\d+)' -ErrorAction SilentlyContinue
    if ($m) { $OdooPort = [int]$m.Matches[0].Groups[1].Value }
  }
  if ($OdooPort -eq 0) {
    $proc = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
      Where-Object { $_.CommandLine -match "odoo-bin" -and $_.CommandLine -match "--http-port=(\d+)" }
    if ($proc) {
      $m = [regex]::Match($proc[0].CommandLine, '--http-port=(\d+)')
      if ($m.Success) { $OdooPort = [int]$m.Groups[1].Value }
    }
  }
  if ($OdooPort -eq 0) { $OdooPort = 8069 }
}
Step "Odoo appears to listen on port $OdooPort"
if (-not $TestUrl) { $TestUrl = "http://localhost:$OdooPort/web/dataset/call_kw" }
if ($TestMB -le 0) { $TestMB = [Math]::Min($NewLimitMB, 150) }

# --- probe helper -----------------------------------------------------------
# Posts a valid JSON-RPC body padded with trailing spaces (valid JSON) so Odoo
# parses the body the same way a real save does. A 413 here is the size cap.
function Test-UploadLimit([string]$Url, [int]$MB) {
  $js = '{"jsonrpc":"2.0","method":"call","params":{"model":"res.users","method":"search_count","args":[[]],"kwargs":{}},"id":1}'
  $target = ($MB * 1MB)
  if ($target -lt $js.Length) { $target = $js.Length }
  $body = $js + (' ' * ($target - $js.Length))
  try {
    $r = Invoke-WebRequest -Uri $Url -Method Post -Body $body `
         -ContentType "application/json" -UseBasicParsing -TimeoutSec 180 -ErrorAction Stop
    return @{ code = $r.StatusCode; text = "accepted a ${MB}MB body (HTTP $($r.StatusCode))" }
  } catch {
    $resp = $_.Exception.Response
    if ($resp) {
      $code = [int]$resp.StatusCode
      if ($code -eq 413) { return @{ code = 413; text = "rejected ${MB}MB with HTTP 413 (limit is below this)" } }
      return @{ code = $code; text = "answered HTTP $code for ${MB}MB (not a 413 -> size was accepted)" }
    }
    return @{ code = 0; text = "no HTTP response: $($_.Exception.Message)" }
  }
}

function Backup-File([string]$Path) {
  $dest = Join-Path $BackupDir ($Path -replace '[:\\\/]', '_')
  Copy-Item -LiteralPath $Path -Destination $dest -Force
  return $dest
}

# --- detect proxies ---------------------------------------------------------
Step "Detecting what sits in front of Odoo"
$found = @()

# nginx
$nginxProcs = Get-Process nginx -ErrorAction SilentlyContinue
$nginxSvc   = Get-Service -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'nginx' }
$nginxExe   = (Get-Command nginx.exe -ErrorAction SilentlyContinue).Source
if (-not $nginxExe -and $nginxProcs) { $nginxExe = $nginxProcs[0].Path }
$nginxConfs = @()
if ($nginxExe) {
  $nginxRoot = Split-Path $nginxExe -Parent
  $nginxConfs = Get-ChildItem -Path $nginxRoot -Recurse -Include *.conf -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -notmatch '\\temp\\' }
}
if ($nginxProcs -or $nginxSvc -or $nginxConfs) {
  $found += "nginx"
  $nginxProxies = $nginxConfs | Where-Object {
    Select-String -Path $_.FullName -Pattern "localhost:$OdooPort|127\.0\.0\.1:$OdooPort|:$OdooPort\b" -Quiet -ErrorAction SilentlyContinue
  }
  if ($nginxProxies) { Ok "nginx detected (exe: $nginxExe) and it proxies port $OdooPort" }
  else { Warn "nginx detected (exe: $nginxExe); no obvious proxy_pass to port $OdooPort" }
}

# IIS
$iis = Get-Service W3SVC -ErrorAction SilentlyContinue
$iisProxiesOdoo = $false
if ($iis) {
  $found += "iis"
  $iisConfigs = @()
  $ah = Join-Path $env:windir "system32\inetsrv\config\applicationHost.config"
  if (Test-Path $ah) { $iisConfigs += $ah }
  if (Test-Path "C:\inetpub") {
    $iisConfigs += @(Get-ChildItem "C:\inetpub" -Recurse -Filter web.config -ErrorAction SilentlyContinue |
                     Select-Object -ExpandProperty FullName)
  }
  $hit = $iisConfigs | Where-Object {
    Select-String -Path $_ -Pattern "localhost:$OdooPort|127\.0\.0\.1:$OdooPort|:$OdooPort\b" -Quiet -ErrorAction SilentlyContinue
  }
  if ($hit) { $iisProxiesOdoo = $true; Ok "IIS detected (W3SVC: $($iis.Status)) and it proxies port $OdooPort" }
  else { Warn "IIS detected (W3SVC: $($iis.Status)) but no proxy rule to port $OdooPort was found" }
}

# Apache
$apache = Get-Service -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'Apache|httpd' }
$apacheExe = (Get-Command httpd.exe -ErrorAction SilentlyContinue).Source
if ($apache -or $apacheExe) { $found += "apache"; Ok "Apache detected" }

if (-not $found) {
  Warn "No reverse proxy found on this machine. The cap may be Odoo itself, or a gateway on another host."
}

# --- baseline probe ---------------------------------------------------------
if (-not $SkipVerify) {
  Step "Baseline: posting ${TestMB}MB to $TestUrl"
  $base = Test-UploadLimit $TestUrl $TestMB
  Info $base.text
}

# --- apply fixes ------------------------------------------------------------
$changed = $false

# nginx
if ($found -contains "nginx") {
  Step "nginx: setting client_max_body_size to ${NewLimitMB}m"
  $target = $nginxConfs | Where-Object { Select-String -Path $_.FullName -Pattern 'server\s*\{|proxy_pass|http\s*\{' -Quiet } |
            Select-Object -First 1
  if (-not $target) { $target = $nginxConfs | Select-Object -First 1 }
  if ($target -and -not $NoApply) {
    $bk = Backup-File $target.FullName
    $text = Get-Content -LiteralPath $target.FullName -Raw
    if ($text -match 'client_max_body_size\s+[^;]+;') {
      $text = $text -replace 'client_max_body_size\s+[^;]+;', "client_max_body_size ${NewLimitMB}m;"
    } else {
      $text = $text -replace '(http\s*\{)', "`$1`r`n    client_max_body_size ${NewLimitMB}m;"
    }
    Set-Content -LiteralPath $target.FullName -Value $text -Encoding UTF8
    Ok "PATCHED $(Split-Path $target.FullName -Leaf)  (backup: $bk)"
    $changed = $true
    if ($nginxSvc) { Restart-Service -Name $nginxSvc.Name -Force; Ok "restarted nginx service" }
    elseif ($nginxExe) { & $nginxExe -s reload 2>&1 | Out-Null; Ok "reloaded nginx" }
  } elseif ($NoApply) { Warn "NoApply: would patch $($target.FullName)" }
  else { Warn "Could not locate an nginx config to edit" }
}

# IIS
if ($found -contains "iis") {
  if (-not $iisProxiesOdoo) {
    Warn "Skipping IIS: it does not appear to forward port $OdooPort."
  } else {
  Step "IIS: setting requestLimits maxAllowedContentLength to $limitBytes bytes"
  $appcmd = Join-Path $env:windir "system32\inetsrv\appcmd.exe"
  if ((Test-Path $appcmd) -and -not $NoApply) {
    $ah = Join-Path $env:windir "system32\inetsrv\config\applicationHost.config"
    if (Test-Path $ah) { $bk = Backup-File $ah; Ok "backup: $bk" }
    & $appcmd set config -section:system.webServer/security/requestFiltering `
        "-requestLimits.maxAllowedContentLength:$limitBytes" /commit:apphost | Out-Null
    # also the older system.web limit (KB)
    & $appcmd set config -section:system.web/httpRuntime "-maxRequestLength:$($NewLimitMB*1024)" /commit:apphost | Out-Null
    Ok "IIS request filtering raised"
    $changed = $true
    Restart-Service W3SVC -Force; Ok "restarted W3SVC"
  } elseif ($NoApply) { Warn "NoApply: would raise IIS request limits" }
  else { Warn "appcmd not found; raise maxAllowedContentLength manually in web.config" }
  }
}

# Apache
if ($found -contains "apache") {
  Step "Apache: setting LimitRequestBody to $limitBytes"
  $conf = if ($apacheExe) { Join-Path (Split-Path $apacheExe -Parent) "conf\httpd.conf" } else { $null }
  if ($conf -and (Test-Path $conf) -and -not $NoApply) {
    $bk = Backup-File $conf
    Add-Content -LiteralPath $conf -Value "`r`nLimitRequestBody $limitBytes"
    Ok "PATCHED httpd.conf (backup: $bk)"
    $changed = $true
    if ($apache) { Restart-Service -Name $apache.Name -Force; Ok "restarted Apache" }
  } elseif ($NoApply) { Warn "NoApply: would add LimitRequestBody" }
  else { Warn "Could not locate httpd.conf" }
}

if (-not $changed -and -not $NoApply) {
  Info "No proxy config was changed."
}

# --- verify -----------------------------------------------------------------
if (-not $SkipVerify) {
  Step "Verifying: posting ${TestMB}MB to $TestUrl"
  Start-Sleep -Seconds 3
  $after = Test-UploadLimit $TestUrl $TestMB
  if ($after.code -eq 413) {
    Warn $after.text
    Warn "If a proxy is still capping it, find it:  netstat -ano | findstr :80"
    Warn "Also test the public URL: -TestUrl http://<server-host>/"
  } else {
    Ok $after.text
  }
  if (-not $found) {
    Warn "No proxy was found in front of Odoo on this machine, so nothing local was changed."
    Warn "Two things to check:"
    Warn "  * a proxy / gateway on ANOTHER host (find it on the client: DevTools > Network > the 413 response 'Server' header)"
    Warn "  * Odoo's own cap - raise it with system parameter 'web.max_file_upload_size' (bytes) in"
    Warn "    Settings > Technical > System Parameters (needs a werkzeug that enforces it, >= 2.3)."
    Warn "Fastest workaround: ingest from a server folder (pack > Server Folder) instead of uploading."
  }
}

Write-Host ""
Write-Host "Done. Backups in $BackupDir" -ForegroundColor Green
Write-Host "Rollback: copy the needed file from the backup folder back over the original and restart the service." -ForegroundColor DarkGray
