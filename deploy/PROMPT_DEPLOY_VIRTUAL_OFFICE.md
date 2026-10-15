# opencode Prompt — Deploy / Update Virtual Office on a Windows Odoo 18 server

Copy and paste this entire block as your prompt to opencode running on the target Windows Server.

---

Deploy (or update) the **Virtual Office** module on this Odoo 18 server. The module lives in the
Zakheni `J18Odoo` repo under `virtual_office_builds\`. Execute the steps below in order.

## Step 1 — Clone or update the repo

```powershell
$repo = "$env:TEMP\J18Odoo"
if (Test-Path "$repo\.git") { git -C $repo pull --ff-only origin master } else { git clone --depth 1 --branch master https://github.com/Zakheni/J18Odoo.git $repo }
```

## Step 2 — Run the deploy script

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\deploy\deploy_virtual_office.ps1" -SourceDir $repo -SkipPull
```

The script:

1. picks the newest build in `virtual_office_builds\`,
2. backs up the currently deployed module to `C:\odoo18\custom-addons\backups\`,
3. copies the build to `C:\odoo18\custom-addons\virtual_office`,
4. stops Odoo, applies the module (`-u virtual_office`), restarts Odoo,
5. waits for `http://localhost:8069/web/login` to return 200 and prints the DB module version.

## Step 3 — Confirm

Expect the last lines to read:

```
    HTTP 200
    DB says: ('18.0.1.5.0', 'installed')
Done. Deployed virtual_office 18.0.1.5.0 from 2026-10-14_build4.
```

## Options

| Option | Effect |
| --- | --- |
| `-Build 2026-10-14_build4` | Deploy a specific build instead of the newest |
| `-Install` | Install (`-i`) instead of upgrade (`-u`) — use on a fresh database |
| `-OdooRoot "D:\odoo18"` | Non-default Odoo root (default `C:\odoo18`) |
| `-ServiceName Odoo18` | Windows service name (default; auto-detected, falls back to process mode) |
| `-NoRestart` | Apply the module but do not stop/start the server |
| `-SourceDir <path>` | Use an existing checkout instead of cloning into `%TEMP%` |

## Rollback

Move the newest folder in `C:\odoo18\custom-addons\backups\` back to
`C:\odoo18\custom-addons\virtual_office`, then re-run with `-NoRestart`.
