# opencode Prompt — Fix CV Studio large-upload error (HTTP 413) on a Windows Odoo 18 server

Copy and paste this entire block as your prompt to opencode on the target Windows Server.

---

On this Odoo 18 server, uploading a CV pack in **CV Studio** fails with
**"The request sent to the server was too large"**. That message is Odoo's web client dialog for an
**HTTP 413** response — something is capping the request body size. Fix it.

> If **CV Studio is not installed, or may be out of date** on this server, deploy the current module
> first — see `deploy/PROMPT_DEPLOY_CV_STUDIO.md` (runs `deploy_cv_studio.ps1`). Then continue below.

## Step 1 — Clone or update the repo

```powershell
$repo = "$env:TEMP\J18Odoo"
if (Test-Path "$repo\.git") { git -C $repo pull --ff-only origin master } else { git clone --depth 1 --branch master https://github.com/Zakheni/J18Odoo.git $repo }
```

## Step 2 — Diagnose first (changes nothing)

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\deploy\fix_cv_studio_upload_limit.ps1" -NoApply
```

Read the output:

- If it reports **nginx / IIS / Apache detected**, that proxy is capping the upload — continue to Step 3.
- If it reports **no reverse proxy found**, the cap is Odoo's own 128 MiB. Then the fix is to ingest
  from a **server folder** instead of uploading (see "If there is no proxy" below).

## Step 3 — Apply the fix

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\deploy\fix_cv_studio_upload_limit.ps1" -NewLimitMB 200
```

The script backs up each config file it edits (under `%TEMP%\cvstudio_limit_backup_*`),
raises the body limit (nginx `client_max_body_size`, IIS `maxAllowedContentLength`, or Apache
`LimitRequestBody`), restarts the proxy, then POSTs a 200 MB probe to confirm the new ceiling.

If the server is reached through a **public hostname / different port**, verify through that:

```powershell
powershell -ExecutionPolicy Bypass -File "$repo\deploy\fix_cv_studio_upload_limit.ps1" -TestUrl "http://<server-host>/" -NewLimitMB 200
```

## Step 4 — Confirm

Expect the last lines to read something like:

```
==> Verifying: posting 150MB to http://localhost:8069/web/login
    answered HTTP 303 for 150MB (not a 413 -> size was accepted)
```

Then reload CV Studio in the browser and upload the pack again.

## If there is no proxy (Odoo's own 128 MiB limit)

Odoo caps request bodies at 128 MiB in code. For a pack larger than that, use the built-in
folder ingest instead of an upload:

1. Copy the pack folder (or unzipped CV folders) onto this server, e.g. `C:\packs\Panel D`.
2. In CV Studio, open the pack and use **Server Folder** (under *Advanced*) instead of drag-and-drop.
3. Also uncheck **Copy finished CVs to a folder on this PC** only if you do not want the outputs on disk.

## Rollback

Copy the needed file from the newest `%TEMP%\cvstudio_limit_backup_*` folder back over the
original, then restart the proxy service.
