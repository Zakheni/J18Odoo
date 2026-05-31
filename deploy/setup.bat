@echo off
title Zakheni Odoo 18 Setup
cd /d "%~dp0"

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...
    powershell start-process "%~f0" -verb runas
    exit /b
)

echo.
echo  ========================================
echo    Zakheni Odoo 18 — Windows Installer
echo  ========================================
echo.
echo  This will install and configure:
echo    - Odoo 18 ERP (community)
echo    - PostgreSQL 17 database
echo    - Python 3.12 virtual environment
echo    - SARS-compliant payroll setup
echo    - Helpdesk per-customer routing
echo    - Partner enrichment from web
echo    - Enterprise accounting features
echo.
echo  Target directory: C:\odoo18
echo.
pause

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %errorlevel% equ 0 (
    echo.
    echo  Setup completed successfully!
    echo  Opening http://localhost:8069 ...
    timeout /t 3 >nul
    start http://localhost:8069
) else (
    echo.
    echo  Setup failed. Check C:\odoo18\init.log for details.
    pause
)
