param(
    [string]$OdooDir = "C:\odoo18",
    [string]$ServiceName = "odoo",
    [string]$DbName = "odoo18",
    [string]$GitRemote = "origin",
    [string]$GitBranch = "master"
)

$ErrorActionPreference = "Stop"
$logFile = Join-Path $OdooDir "deploy_tenders.log"

function Log { param([string]$Msg) $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"; "$ts $Msg" | Tee-Object -FilePath $logFile -Append }

Log "=== Zakheni Tenders Deployment ==="

# Step 1: Stop Odoo service
Log "Stopping Odoo service ($ServiceName)..."
try {
    Stop-Service -Name $ServiceName -Force -ErrorAction Stop
    Start-Sleep -Seconds 5
    Log "Service stopped."
} catch {
    Log "WARNING: Could not stop service: $_"
    Log "Attempting to kill python processes..."
    Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 3
}

# Step 2: Pull latest from GitHub
Log "Pulling latest from GitHub ($GitRemote/$GitBranch)..."
Set-Location -LiteralPath $OdooDir\custom-addons
& "C:\Program Files\Git\bin\git.exe" fetch $GitRemote $GitBranch 2>&1 | ForEach-Object { Log $_ }
& "C:\Program Files\Git\bin\git.exe" reset --hard "$GitRemote/$GitBranch" 2>&1 | ForEach-Object { Log $_ }
Log "Git pull complete."

# Step 3: Run module upgrade
Log "Running module upgrade: -u zakheni_tender..."
$upgradeLog = Join-Path $OdooDir "upgrade_zakheni_tender.log"
$process = Start-Process -NoNewWindow -FilePath "$OdooDir\venv\Scripts\python.exe" `
    -ArgumentList "$OdooDir\server\odoo-bin", "-c", "$OdooDir\odoo.conf", "-d", $DbName, "-u", "zakheni_tender", "--stop-after-init" `
    -RedirectStandardOutput $upgradeLog -RedirectStandardError $upgradeLog -PassThru
$process.WaitForExit()
Log "Upgrade exit code: $($process.ExitCode)"
Get-Content $upgradeLog -Tail 10 | ForEach-Object { Log "  $_" }

# Step 4: Restart Odoo service
Log "Restarting Odoo service ($ServiceName)..."
Start-Service -Name $ServiceName -ErrorAction Stop
Start-Sleep -Seconds 10
$svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($svc.Status -eq "Running") {
    Log "Service is RUNNING."
} else {
    Log "ERROR: Service status is $($svc.Status). Check logs."
}

Log "=== Deployment complete ==="
