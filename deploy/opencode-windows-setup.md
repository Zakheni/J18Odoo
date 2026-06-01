# Zakheni Odoo 18 — Windows Server Setup for opencode

Give this file to opencode running on the target Windows Server.
It will execute each step in order.

## Step 1: Create working directory

```powershell
$OdooDir = "C:\odoo18"
New-Item -ItemType Directory -Path $OdooDir -Force
New-Item -ItemType Directory -Path "$OdooDir\custom-addons" -Force
New-Item -ItemType Directory -Path "$OdooDir\data" -Force
```

## Step 2: Download and install PostgreSQL 17 via winget

```powershell
# Install PostgreSQL
winget install -e --id PostgreSQL.PostgreSQL.17 --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null

# Wait for install, then set password
$pgBin = "$env:ProgramFiles\PostgreSQL\17\bin"
$env:Path = "$pgBin;$env:Path"

# Set password for postgres user
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'openpgpwd';" 2>$null
psql -U postgres -c "CREATE USER openpg WITH PASSWORD 'openpgpwd' CREATEDB SUPERUSER;" 2>$null
psql -U postgres -c "CREATE DATABASE odoo18 OWNER openpg;" 2>$null
```

## Step 3: Install Python and Git via winget

```powershell
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
```

## Step 4: Clone Odoo 18 source

```powershell
$serverDir = "$OdooDir\server"
git clone --depth 1 --branch 18.0 https://github.com/odoo/odoo.git $serverDir
```

## Step 5: Clone Zakheni custom modules

```powershell
git clone --depth 1 --branch master https://github.com/Zakheni/J18Odoo.git "$env:TEMP\J18Odoo"
Copy-Item "$env:TEMP\J18Odoo\*" "$OdooDir\custom-addons\" -Recurse -Force
Remove-Item "$env:TEMP\J18Odoo" -Recurse -Force
```

## Step 6: Create Python venv and install dependencies

```powershell
$venvDir = "$OdooDir\venv"
python -m venv $venvDir
$python = "$venvDir\Scripts\python.exe"
$pip = "$venvDir\Scripts\pip.exe"

& $pip install --upgrade pip wheel setuptools
& $pip install -r "$serverDir\requirements.txt"
& $pip install google-api-python-client office365-rest-python-client
```

## Step 7: Build addons path

```powershell
$addonsPath = @()
$addonsPath += "$serverDir\odoo\addons"
Get-ChildItem "$OdooDir\custom-addons" -Directory | Sort-Object Name | ForEach-Object {
    $addonsPath += $_.FullName
}
$addonsPathStr = $addonsPath -join ","
```

## Step 8: Create odoo.conf

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

## Step 9: Initialize database

```powershell
# Install base modules
& $python "$serverDir\odoo-bin" -c "$OdooDir\odoo.conf" -d odoo18 -i base --without-demo=all --stop-after-init

# Install custom modules
& $python "$serverDir\odoo-bin" -c "$OdooDir\odoo.conf" -d odoo18 `
    -i zakheni_config,zakheni_helpdesk,zakheni_partner_enrich,zakheni_accounting `
    --without-demo=all --stop-after-init
```

## Step 10: Download NSSM and create Windows service

```powershell
$nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
$nssmZip = "$env:TEMP\nssm.zip"
try {
    Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -UseBasicParsing
} catch {
    Invoke-WebRequest -Uri "https://github.com/nicedoc/nssm/releases/download/v2.24/nssm-2.24.zip" -OutFile $nssmZip -UseBasicParsing
}
Expand-Archive -Path $nssmZip -DestinationPath "$env:TEMP\nssm" -Force
$nssmPath = "$OdooDir\nssm.exe"
Copy-Item "$env:TEMP\nssm\nssm-2.24\win64\nssm.exe" $nssmPath
Remove-Item "$env:TEMP\nssm" -Recurse -Force
Remove-Item $nssmZip -Force

# Create service
& $nssmPath stop Odoo18 2>$null | Out-Null
& $nssmPath remove Odoo18 confirm 2>$null | Out-Null
$odooArgs = "-c", "$OdooDir\odoo.conf"
& $nssmPath install Odoo18 $python "$serverDir\odoo-bin" $odooArgs
& $nssmPath set Odoo18 AppDirectory $serverDir
& $nssmPath set Odoo18 DisplayName "Odoo 18 - Zakheni ICT"
& $nssmPath set Odoo18 Start SERVICE_AUTO_START
& $nssmPath set Odoo18 AppStdout "$OdooDir\odoo.log"
& $nssmPath set Odoo18 AppStderr "$OdooDir\odoo-error.log"
& $nssmPath set Odoo18 AppRotateFiles 1
& $nssmPath set Odoo18 AppRotateOnline 1
& $nssmPath set Odoo18 AppRotateSeconds 86400
& $nssmPath set Odoo18 AppRotateBytes 10485760
& $nssmPath start Odoo18
```

## Step 11: Verify

```powershell
Start-Sleep -Seconds 10
curl.exe -s -o nul -w "%{http_code}" http://localhost:8069
```

If it returns `200`, Odoo is running. Log in at `http://localhost:8069` with `admin` / `admin`.

## If opencode has trouble with winget (no GUI)

On Server Core or systems without winget, replace Step 2 and 3 with direct downloads:

```powershell
# PostgreSQL direct download
Invoke-WebRequest -Uri "https://get.enterprisedb.com/postgresql/postgresql-17.2-1-windows-x64.exe" -OutFile "$env:TEMP\pg-installer.exe" -UseBasicParsing
Start-Process "$env:TEMP\pg-installer.exe" -ArgumentList "--mode unattended --prefix `"$env:ProgramFiles\PostgreSQL\17`" --superpassword openpgpwd --servicename postgresql_17 --serverport 5432" -Wait

# Python direct download
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" -OutFile "$env:TEMP\py-installer.exe" -UseBasicParsing
Start-Process "$env:TEMP\py-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait

# Git direct download
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/Git-2.48.1-64-bit.exe" -OutFile "$env:TEMP\git-installer.exe" -UseBasicParsing
Start-Process "$env:TEMP\git-installer.exe" -ArgumentList "/VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEAPPLICATIONS /COMPONENTS=`"gitlfs`"" -Wait
```
