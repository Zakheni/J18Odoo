# Document Management System (DMS) — User Guide

**Module:** OCA dms (v18.0)  
**Repository:** https://github.com/OCA/dms  
**Author:** MuK IT, Tecnativa, Odoo Community Association (OCA)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Installation & Dependencies](#2-installation--dependencies)
3. [Core Concepts: Storages, Directories & Files](#3-core-concepts-storages-directories--files)
4. [Configuration](#4-configuration)
   - 4.1 Creating a Storage
   - 4.2 Creating Access Groups
   - 4.3 Creating Directories (Folders)
   - 4.4 Tags & Categories
5. [Working with Files](#5-working-with-files)
   - 5.1 Uploading Files
   - 5.2 Managing Files
   - 5.3 Searching & Filtering
6. [Access Control](#6-access-control)
   - 6.1 Access Groups & Permissions
   - 6.2 Portal Access & Sharing
7. [Version Control](#7-version-control)
8. [Storage Migration](#8-storage-migration)
9. [Auto-Classification](#9-auto-classification)
10. [Integration with Other Modules](#10-integration-with-other-modules)
11. [Troubleshooting & FAQ](#11-troubleshooting--faq)

---

## 1. Overview

The **Document Management System (DMS)** is an OCA module that provides a complete document management solution inside Odoo. It lets you:

- Create and organize files in a hierarchical folder (directory) structure.
- Upload files individually, in bulk, or via drag‑and‑drop.
- Control access with fine‑grained group permissions (read, create, write, delete).
- Categorize documents with tags and color codes.
- Track file versions and restore previous revisions.
- Share documents internally, with portal users, or via public tokenized links.
- Integrate with any Odoo model (Sales, Purchase, Projects, HR, etc.).
- Automatically classify incoming `.zip` archives into the correct directories.

> **Tip:** The DMS is the foundation for an ecosystem of addon modules (`dms_field`, `dms_auto_classification`, `dms_user_role`, etc.). Install only the modules you need.

---

## 2. Installation & Dependencies

### Required

| Module | Technical Name | Source |
|--------|---------------|--------|
| Document Management System | `dms` | OCA/dms |
| Mail Preview Base | `mail_preview_base` | OCA/social (required for file previews) |

### Optional but Recommended

| Module | Purpose |
|--------|---------|
| `mail_preview` (all submodules) | Better file preview support |
| `dms_field` | Embed a DMS folder tree directly inside any record form |
| `dms_auto_classification` | Auto‑classify `.zip` files into DMS directories |
| `dms_field_auto_classification` | Auto‑classify into embedded DMS fields |
| `dms_user_role` | Additional user‑role based permissions |
| `hr_dms_field` | Add DMS field to employee records |
| `web_editor_media_dialog_dms` | Insert DMS files into the web editor media dialog |

### Installation Steps

1. Go to **Apps** → search for **Document Management System**.
2. Click **Install**.
3. Install any additional modules you need (e.g., `dms_auto_classification`).
4. Restart the Odoo server if prompted.

> **Note:** The `python-magic` library is recommended on the server for full file‑type detection. Install it with `pip install python-magic`.

---

## 3. Core Concepts: Storages, Directories & Files

```
Storage (physical backend)
 └── Directory (root folder)
      ├── Sub‑directory
      │    └── File
      ├── Sub‑directory
      └── File
```

| Concept | Description |
|---------|-------------|
| **Storage** | Defines **where** files are physically saved (Database, Attachment, or File system). |
| **Directory** | A folder that organises files. Can be nested. Has its own access‑control groups. |
| **File** | An individual document with content, metadata, tags, and version history. |

---

## 4. Configuration

Configure the DMS before uploading documents.

### 4.1 Creating a Storage

1. Go to **Documents → Configuration → Storages**.
2. Click **Create**.
3. Fill in the fields:

   | Field | Description |
   |-------|-------------|
   | **Name** | e.g., "Company Documents" |
   | **Save Type** | Choose how files are physically stored. Options are: <br>• **Database** – files stored as binary fields in the database (backup‑friendly).<br>• **Attachment** – files stored as Odoo `ir.attachment` records.<br>• **File** – files stored on the server file‑system. |
   | **Inherit Access From Related Record** | If enabled (and when using `dms_field`), directory permissions are inherited from the linked business record. |

4. Click **Save**.

> **Tip:** Start with **Attachment** mode — it is the most flexible and works well with Odoo's built‑in attachment features.

### 4.2 Creating Access Groups

Access Groups define who can see and manipulate directories and their contents.

1. Go to **Documents → Configuration → Access Groups**.
2. Click **Create**.
3. Enter a **Name** (e.g., "DMS Administrators").
4. Enable the permissions:

   | Permission | Meaning |
   |-----------|---------|
   | **Create** | Can create new files and sub‑directories. |
   | **Write** | Can edit file content / metadata. |
   | **Unlink** | Can delete files and directories. |
   | **Read** | Always enabled (cannot be disabled). |

5. Add **Users** to the group.
6. Click **Save**.

Repeat for additional groups (e.g., "DMS Read‑Only", "DMS Editors").

### 4.3 Creating Directories (Folders)

1. Go to **Documents → Directories**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |-------|-------------|
   | **Name** | e.g., "Contracts" |
   | **Parent Directory** | Leave empty for a root‑level folder. |
   | **Storage** | Select the storage created in step 4.1. |
   | **Is Root** | Check this to mark it as a top‑level directory. |

4. Go to the **Groups** tab. Add access groups and set their permissions:

   - **Read**: See the directory and its files.
   - **Create**: Add files / sub‑directories.
   - **Write**: Modify files / directory metadata.
   - **Delete**: Remove files or the directory itself.

5. Click **Save**.

> **Tip:** Nest directories for a logical hierarchy: `Contracts / 2025 / NDAs / VendorA`.

### 4.4 Tags & Categories

Tags provide a lightweight, cross‑folder way to categorise files.

#### Creating Tags

1. Go to **Documents → Configuration → Tags**.
2. Click **Create**.
3. Enter:
   - **Name** — e.g., "Confidential", "Expired", "Pending Review"
   - **Color** — pick a colour for visual grouping
   - **Tooltip** — optional description that appears on hover
4. Click **Save**.

#### Using Tags

- Open any **File** or **Directory** form.
- Under the **Tags** field, select one or more existing tags.
- Tags appear as coloured badges in list/kanban views.
- Filter files by tag using the **Filters** menu or search bar.

> **Tip:** Combine tags with folder location — e.g., place a file in `Invoices/2025` and tag it "Paid" and "Audited".

---

## 5. Working with Files

### 5.1 Uploading Files

#### Single Upload

1. Go to **Documents → Files**.
2. Click **Create**.
3. Fill in:
   - **Name** (auto‑filled from the file name)
   - **Directory** — choose the target folder
   - **Content** — click **Upload** and select a file from your computer
4. Optionally add **Tags**, **Description**, or other metadata.
5. Click **Save**.

#### Bulk Upload (Drag & Drop)

1. Go to **Documents** main menu (the tree/kanban view).
2. Drag one or more files from your file explorer directly onto the Odoo interface.
3. A dialog appears — select the target **Directory** and any **Tags**.
4. Click **Upload**.
5. Files are created individually with the uploaded content.

> **Tip:** You can also drag entire folders — each folder becomes a DMS directory.

#### Upload via Chatter

When you attach a file to any Odoo record (e.g., a Sales Order), you can link that attachment to a DMS directory:

1. Open any record (e.g., SO#1234).
2. In the **Chatter**, click 📎 **Attach**.
3. Click **Link to DMS** (if using `dms_field`).
4. Select the target directory.
5. The file appears both as an attachment *and* inside the DMS folder.

### 5.2 Managing Files

| Action | How To |
|--------|--------|
| **Rename** | Open the file → edit the **Name** field → Save. |
| **Move** | Open the file → change the **Directory** field → Save. |
| **Download** | Click the file name link or the **Download** button in the form. |
| **Delete** | Use the **Action** dropdown → **Delete** (requires Unlink permission). |
| **Edit Content** | Replace the **Content** field with a new file upload (creates a version when versioning is enabled). |
| **Add Tags** | Open the file → select tags in the **Tags** field → Save. |
| **Share** | Click the **Share** button to generate a public tokenized link (see section 6.2). |

### 5.3 Searching & Filtering

Use the search bar at the top of the **Documents → Files** view:

- **Full‑text search** — searches file names and content metadata.
- **Filters** — filter by Directory, Tags, Owner, Storage, or Creation Date.
- **Group By** — group by Directory, Tags, or Owner.

> **Tip:** Save frequently used searches as **Favorites** using the star icon.

---

## 6. Access Control

### 6.1 Access Groups & Permissions

DMS access control works at **two levels**:

1. **Storage Level** — who can see/modify the storage itself (Odoo security groups).
2. **Directory Level** — per‑folder permissions via DMS Access Groups.

**Permission Matrix (per directory):**

| Permission | What the user can do |
|-----------|---------------------|
| **Read** | View the directory and list its files. |
| **Create** | Upload new files and create sub‑directories. |
| **Write** | Edit file metadata, rename files, move files. |
| **Delete** | Remove files and destroy the directory. |

Users can belong to multiple groups for cumulative permissions.

### 6.2 Portal Access & Sharing

#### Grant Portal Access

1. Create or edit a DMS **Access Group** (see 4.2).
2. Add the portal user to the group.
3. On the **Directory** form → **Groups** tab → add that group with the desired permissions.
4. When the portal user logs into the **Portal**, they see the shared directories and can browse/download files (permissions depending).

#### Public Sharing (Tokenized Links)

1. Open a **Directory** or **File**.
2. Click the **Share** button.
3. Toggle **Share Link** to active.
4. Copy the generated URL.
5. Anyone with this link can access the resource — **no login required**.

> **Warning:** Token links bypass authentication. Only share with trusted parties. Revoke access by deactivating the toggle.

---

## 7. Version Control

Version control lets you track changes to a file's content over time.

> **Note:** Version control is currently supported for **Database** and **File** storage types, **not** for Attachment storage.

### Enabling Versioning

Enable versioning at the level that suits your workflow:

| Level | Where to Enable |
|-------|----------------|
| **Storage** | **Documents → Configuration → Storages** → check **Allow Versioning**. All directories in this storage inherit the setting. |
| **Directory** | Open a Directory → check **Allow Versioning**. Overrides the storage setting. |
| **File** | Open a File → check **Allow Versioning**. Overrides the directory setting. |

> **Tip:** Changes to versioning settings are tracked in the chatter.

### Creating a New Version

1. Open a file that has versioning enabled.
2. In the **Content** field, upload a new file.
3. The system automatically:
   - Archives the old file (`active = False`).
   - Creates a new file (`active = True`) as the current version.
   - Links the new file's **Parent** to the old one.
   - Links both to the shared **Origin** file (the very first version).
   - Increments the **Version Number**.
   - Posts a chatter message on all related files with the history.

### Viewing & Restoring Versions

- **List all versions**: Go to **Documents → Files** → use the filter **Archived Files**.
- **Restore a version**: Open the archived file → click **Restore**. The restored file becomes active, and the previously active version is archived.

> **Note:** Archived (inactive) files are **read‑only** — you cannot create new versions from them. Use **Restore** first.

---

## 8. Storage Migration

If you need to change a storage's **Save Type** (e.g., from Database to Attachment), you must migrate the file data.

### Full Migration

1. Go to **Documents → Configuration → Storages**.
2. Select the storage you want to modify.
3. Change the **Save Type**.
4. Click the **Migrate Files** button.
5. All files in that storage are migrated at once.

### Manual (Per‑File) Migration

1. Same as above, but click **Manual File Migration** instead.
2. Choose individual files to migrate.
3. Process them one by one.

### Migration Queue

- Go to **Documents → Configuration → Migration**.
- View all files that still need migration across all storages.
- Migrate them manually from this central view.

> **Warning:** Migration is a data‑intensive operation. Take a database backup before migrating large storages.

---

## 9. Auto-Classification

The **`dms_auto_classification`** module automatically sorts files inside a `.zip` archive into the correct DMS directories.

### Configuration: Classification Templates

1. Go to **Documents → Configuration → Classification Templates**.
2. Click **Create**.
3. Set **Name** (e.g., "Client Documents Routing").
4. Add **Lines** with:

   | Field | Description | Example |
   |-------|-------------|---------|
   | **Filename Pattern** | Regex to match file names inside the `.zip`. | `\.pdf$` — matches all PDFs |
   | **Directory Pattern** | Path of the target DMS directory. Use `/` as separator. | `Documents / Contracts` |
   | **Model** (optional) | For `dms_field_auto_classification`: link to a business model (e.g., `res.partner`). | `res.partner` |
   | **Detail** (optional) | Field reference to match against the record (e.g., `vat`). | `vat` |

**Pattern Tips:**
- If the directory path **does not** contain `/`, DMS searches all sub‑directories.
- Use `{0}` in the directory pattern to substitute a value from the matched record (e.g., partner name).

### Running Auto-Classification

1. Go to **Documents → Auto Classification**.
2. Select a **Template**.
3. Upload a **.zip file**.
4. Click **Analyze**.
   - DMS extracts the file list and matches each file against the template rules.
   - Each matched line shows the source file and the target directory.
5. Click **Classify**.
   - Files are created as `dms.file` records in their respective directories.
   - A confirmation shows how many files were classified.

> **Tip:** Always run **Analyze** first and review the matches before clicking **Classify**.

---

## 10. Integration with Other Modules

### 10.1 dms_field — Embed DMS in Any Form

The `dms_field` module adds a new **DMS Field** widget that embeds a directory tree directly into any Odoo record form.

**Usage:**
1. A developer adds a `dms_field` to the model's view (e.g., `field_name = dms.Field(...)`).
2. Users see a mini file‑manager inside the record.
3. Files uploaded there are automatically linked to the record.

**Integrations that include this:**
- `hr_dms_field` — embeds DMS in Employee forms.
- `dms_field_auto_classification` — auto‑classify into embedded DMS fields.

### 10.2 dms_user_role — Role‑Based Permissions

Adds user‑role records that can be assigned to DMS groups for more flexible permission management.

### 10.3 web_editor_media_dialog_dms

Allows users to browse and insert DMS files directly when editing HTML content with the Odoo web editor (e.g., in website pages, email templates, or knowledge articles).

### 10.4 Odoo Core Documents vs OCA DMS

| Feature | Odoo 18 Core Documents | OCA DMS |
|---------|----------------------|---------|
| Hierarchical folders | Limited (tags‑based grouping) | Full directory tree |
| Access control | Workspace‑level | Per‑directory groups with 4 permissions |
| Storage backends | One type | Database, Attachment, File |
| Version control | Basic | Full version history with restore |
| Auto‑classification | Not available | `dms_auto_classification` |
| Portal sharing | Share per document | Tokenized links per file or folder |

---

## 11. Troubleshooting & FAQ

### Q: Files are not showing up in the portal.
**A:** Ensure the portal user is added to a DMS Access Group, and that group is assigned to the directory with at least **Read** permission.

### Q: I changed the storage `Save Type`. Where are my files?
**A:** The files remain in the old storage until you run a **Migration** (see section 8). They will not be visible until migrated.

### Q: The **Share** link doesn't work.
**A:** Verify the external user does not need a login. Token links should be accessible anonymously. If the link redirects to a login page, check the **Share** toggle is active and the file/directory is not restricted by IP or other firewalls.

### Q: Versioning is greyed out.
**A:** Versioning is only available for **Database** and **File** storage types. Change the storage's **Save Type** first.

### Q: How do I delete a directory that still contains files?
**A:** You must first delete (or move) all files inside it. The system will warn you if a directory is not empty.

### Q: Can I recover a deleted file?
**A:** If you have the **Unlink** permission, files are hard-deleted unless a backup exists. Restore from the database backup.

### Q: Auto-classification says "No matches found".
**A:** Check your regex patterns. Test them against the actual file names in the `.zip`. Remember that patterns are case‑sensitive by default.

---

> **Document Version:** 1.0 — Odoo 18.0 / OCA dms 18.0.1.0.8  
> **Last Updated:** July 2026
