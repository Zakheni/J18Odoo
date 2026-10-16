# opencode Prompt — Deploy / Update CV Studio on a Windows Odoo 18 server

Copy and paste this entire block as your prompt to opencode running on the target Windows Server.

---

Deploy (or update) the **CV Studio** module on this Odoo 18 server. The module lives in the
Zakheni `J18Odoo` repo under `cv_studio\`. Execute the steps below in order.

## Step 1 — Clone or update the repo

```powershell
$repo = "$env:TEMP\J18Odoo"
if (Test-Path "$repo\.git") { git -C $repo pull --ff-only origin master } else { git clone --depth 1 --branch master https://github.com/Zakheni/J18Odoo.git $repo }
```

## Step 2 — Run the deploy script

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\deploy\deploy_cv_studio.ps1" -SourceDir $repo -SkipPull
```

The script:

1. locates the `cv_studio` module in the repo,
2. installs its Python dependencies (`python-docx`, `pymupdf`, `openpyxl`, `pillow`, `pywin32`) into the Odoo virtualenv,
3. backs up the currently deployed module to `C:\odoo18\custom-addons\backups\`,
4. copies the module to `C:\odoo18\custom-addons\cv_studio`,
5. stops Odoo, installs it on a fresh DB or upgrades it (`-i` / `-u` auto-detected), restarts Odoo,
6. waits for `http://localhost:8069/web/login` to return 200 and prints the DB module state.

## Step 3 — Confirm

Expect the last lines to read:

```
    HTTP 200
    DB state now: installed
Done. Deployed cv_studio 18.0.1.0.0.
```

## Requirements on the target machine

- Odoo 18 running from a virtualenv (default `C:\odoo18`).
- **Microsoft Word installed** — the engine uses Word COM automation to convert DOCX → PDF.
- Optional but recommended for AI drafting: an `opencode` executable. Pass its path with
  `-OpenCodeExe "C:\path\to\opencode.exe"`, or set it later in
  **CV Studio → Configuration → Settings → opencode Executable**.

## Options

| Option | Effect |
| --- | --- |
| `-Install` | Force install (`-i`) instead of the auto-detected upgrade (`-u`) |
| `-OpenCodeExe "C:\path\opencode.exe"` | Write the `cv_studio.opencode_exe` setting during deploy |
| `-SkipDeps` | Do not pip-install the Python dependencies into the venv |
| `-OdooRoot "D:\odoo18"` | Non-default Odoo root (default `C:\odoo18`) |
| `-ServiceName Odoo18` | Windows service name (default; auto-detected, falls back to process mode) |
| `-NoRestart` | Apply the module but do not stop/start the server |
| `-SourceDir <path>` | Use an existing checkout instead of cloning into `%TEMP%` |

## Output location

Once running, **Generate CVs** copies the finished CVs to a real folder on the server PC:

```
%USERPROFILE%\Downloads\CV Studio\<pack name>\<role>\<name>\
```

Change this in **CV Studio → Configuration → Settings → Output Folder**. Users can also
download a single CV (PDF/DOCX) or the whole pack as a ZIP straight from the browser.

## Rollback

Move the newest folder in `C:\odoo18\custom-addons\backups\` back to
`C:\odoo18\custom-addons\cv_studio`, then re-run with `-NoRestart`.
