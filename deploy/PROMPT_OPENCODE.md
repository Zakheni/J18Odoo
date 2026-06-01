# opencode Prompt — Windows Server Setup

Copy and paste this entire block as your prompt to opencode running on the target Windows Server.

---

Set up Odoo 18 with Zakheni ICT custom modules on this Windows Server. Execute each step below in order:

## Step 1
```powershell
$OdooDir = "C:\odoo18"
New-Item -ItemType Directory -Path $OdooDir -Force, "$OdooDir\custom-addons" -Force, "$OdooDir\data" -Force
```

## Step 2 — Install PostgreSQL 17
```powershell
Invoke-WebRequest -Uri "https://get.enterprisedb.com/postgresql/postgresql-17.2-1-windows-x64.exe" -OutFile "$env:TEMP\pg-installer.exe" -UseBasicParsing
Start-Process "$env:TEMP\pg-installer.exe" -ArgumentList '--mode unattended', '--prefix "C:\Program Files\PostgreSQL\17"', '--superpassword openpgpwd', '--servicename postgresql_17', '--serverport 5432' -Wait
```

## Step 3 — Configure PostgreSQL users
```powershell
$env:Path = "C:\Program Files\PostgreSQL\17\bin;$env:Path"
psql -U postgres -c "CREATE USER openpg WITH PASSWORD 'openpgpwd' CREATEDB SUPERUSER;" 2>$null
psql -U postgres -c "CREATE DATABASE odoo18 OWNER openpg;" 2>$null
```

## Step 4 — Install Python and Git
```powershell
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" -OutFile "$env:TEMP\py-installer.exe" -UseBasicParsing
Start-Process "$env:TEMP\py-installer.exe" -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_test=0' -Wait

Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/Git-2.48.1-64-bit.exe" -OutFile "$env:TEMP\git-installer.exe" -UseBasicParsing
Start-Process "$env:TEMP\git-installer.exe" -ArgumentList '/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-', '/CLOSEAPPLICATIONS', '/COMPONENTS=gitlfs' -Wait
```

Refresh PATH then:
```powershell
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
```

## Step 5 — Clone Odoo 18
```powershell
$serverDir = "$OdooDir\server"
git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git $serverDir
```

## Step 6 — Clone Zakheni modules
```powershell
git clone --depth 1 --branch master https://github.com/Zakheni/J18Odoo.git "$env:TEMP\J18Odoo"
Copy-Item "$env:TEMP\J18Odoo\*" "$OdooDir\custom-addons" -Recurse -Force
Remove-Item "$env:TEMP\J18Odoo" -Recurse -Force
```

## Step 7 — Python venv and deps
```powershell
$venvDir = "$OdooDir\venv"
python -m venv $venvDir
$python = "$venvDir\Scripts\python.exe"
$pip = "$venvDir\Scripts\pip.exe"
& $pip install --upgrade pip wheel setuptools
& $pip install -r "$serverDir\requirements.txt"
& $pip install google-api-python-client office365-rest-python-client
```

## Step 8 — Build addons_path
```powershell
$addonsPath = @("$serverDir\odoo\addons")
Get-ChildItem "$OdooDir\custom-addons" -Directory | Sort-Object Name | ForEach-Object { $addonsPath += $_.FullName }
$addonsPathStr = $addonsPath -join ","
```

## Step 9 — Create odoo.conf
```powershell
@"
[options]
db_host = localhost
db_port = 5432
db_user = openpg
db_password = openpgpwd
db_name = odoo18
addons_path = $addonsPathStr
data_dir = $OdooDir\data
admin_passwd = admin
list_db = True
workers = 2
max_cron_threads = 2
log_level = info
"@ | Out-File -FilePath "$OdooDir\odoo.conf" -Encoding utf8
```

## Step 10 — Initialize database
```powershell
& $python "$serverDir\odoo-bin" -c "$OdooDir\odoo.conf" -d odoo18 -i base --without-demo=all --stop-after-init
```
```powershell
& $python "$serverDir\odoo-bin" -c "$OdooDir\odoo.conf" -d odoo18 -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting --without-demo=all --stop-after-init
```

## Step 11 — Create Windows service
```powershell
Invoke-WebRequest -Uri "https://github.com/nicedoc/nssm/releases/download/v2.24/nssm-2.24.zip" -OutFile "$env:TEMP\nssm.zip" -UseBasicParsing
Expand-Archive -Path "$env:TEMP\nssm.zip" -DestinationPath "$env:TEMP\nssm" -Force
Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" "$OdooDir\nssm.exe"
Remove-Item "$env:TEMP\nssm" -Recurse -Force, "$env:TEMP\nssm.zip" -Force

$nssm = "$OdooDir\nssm.exe"
& $nssm stop Odoo18 2>$null | Out-Null
& $nssm remove Odoo18 confirm 2>$null | Out-Null
& $nssm install Odoo18 $python "$serverDir\odoo-bin" "-c", "$OdooDir\odoo.conf"
& $nssm set Odoo18 AppDirectory $serverDir
& $nssm set Odoo18 DisplayName "Odoo 18 - Zakheni ICT"
& $nssm set Odoo18 Start SERVICE_AUTO_START
& $nssm set Odoo18 AppStdout "$OdooDir\odoo.log"
& $nssm set Odoo18 AppStderr "$OdooDir\odoo-error.log"
& $nssm set Odoo18 AppRotateFiles 1
& $nssm set Odoo18 AppRotateOnline 1
& $nssm set Odoo18 AppRotateSeconds 86400
& $nssm set Odoo18 AppRotateBytes 10485760
& $nssm start Odoo18
```

## Step 12 — Verify
```powershell
Start-Sleep -Seconds 15
curl.exe -s http://localhost:8069 | Select-String -Pattern "Odoo" -SimpleMatch
Write-Host "Open http://localhost:8069 - login: admin / admin"
```
