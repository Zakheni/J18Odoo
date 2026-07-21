# Odoo 18 Knowledge — User Guide

## Table of Contents

1. [Overview](#1-overview)
2. [Pages (Wiki)](#2-pages-wiki)
   - [2.1 Creating a New Page](#21-creating-a-new-page)
   - [2.2 Organizing Pages into Categories](#22-organizing-pages-into-categories)
   - [2.3 Editing Page Content](#23-editing-page-content)
   - [2.4 Viewing Page History and Revisions](#24-viewing-page-history-and-revisions)
   - [2.5 Linking Pages Together (References)](#25-linking-pages-together-references)
   - [2.6 Tagging Pages](#26-tagging-pages)
3. [Documents (Attachments)](#3-documents-attachments)
   - [3.1 Uploading Files](#31-uploading-files)
   - [3.2 Organizing Files into Folders](#32-organizing-files-into-folders)
   - [3.3 Viewing Documents](#33-viewing-documents)
   - [3.4 Searching and Filtering Documents](#34-searching-and-filtering-documents)
   - [3.5 Grouping Documents](#35-grouping-documents)
   - [3.6 Previewing Attachments](#36-previewing-attachments)
   - [3.7 Downloading Multiple Files as ZIP](#37-downloading-multiple-files-as-zip)
4. [Access Control](#4-access-control)
   - [4.1 Page Access Groups](#41-page-access-groups)
   - [4.2 User / Group Permissions](#42-user--group-permissions)
5. [Best Practices](#5-best-practices)
6. [Common Tasks](#6-common-tasks)

---

## 1. Overview

The **Knowledge** module turns Odoo into a full-fledged company wiki **and** document hub in one place. It is built around two core ideas:

| Feature | What it does |
|---|---|
| **Wiki Pages** | Write rich-text articles, organise them in a category tree, track every revision, cross-link pages, and tag content. |
| **Documents** | Upload any file, assign it to a folder (which is really a wiki category), preview it, search by model or folder, and download multiple files as a ZIP. |

The two sides are connected: the **folder** you see on a document is actually a **wiki category** (`document.page` with `type = "category"`). This means your wiki's table of contents doubles as your document filing system.

---

## 2. Pages (Wiki)

### 2.1 Creating a New Page

Every page has a **type** — this is the most important choice you make.

| Type | Purpose |
|---|---|
| **Content** | A real wiki article with an HTML body. This is what most pages should be. |
| **Category** | A container / folder. It has no editable body of its own — instead it auto-generates an index of its child pages. Use categories to build your hierarchy. |

**To create a Content page:**

1. Go to **Knowledge → Pages → Pages**.
2. Click **New**.
3. Give it a **Title**.
4. Leave the **Type** as "Content".
5. Pick a **Category** (parent). Every content page must live under a category.
6. Fill in the **Revision Name** (e.g. "Rev 01") and **Summary** (e.g. "Initial version").
7. Write your content in the HTML editor.
8. Click **Save**.

**To create a Category page:**

1. Go to **Knowledge → Pages → Categories**.
2. Click **New**.
3. Give it a **Name**.
4. The **Type** defaults to "Category".
5. Optionally pick a **parent Category** to nest it.
6. Optionally set a **Template** — this HTML template will be auto-loaded into every new content page created inside this category.
7. Click **Save**.

> **Tip:** Use the **Browse Wiki Content** menu item (the first entry under Knowledge) for a Kanban view that shows categories as folders and lets you drill into them.

### 2.2 Organizing Pages into Categories

The hierarchy works through the **parent_id** field on each page:

- A **Category** page can be a child of another Category (nesting folders).
- A **Content** page must have a parent Category (it cannot sit at the root).
- You can re-parent a page at any time by editing its **Category** field.

To see the full tree, use **Knowledge → Pages → Categories** in list view. You can group by parent to see the shape of your wiki.

> **Warning:** You cannot create circular parent/child relationships. Odoo prevents this automatically.

### 2.3 Editing Page Content

1. Open the page you want to edit.
2. Click the **Edit** button (pencil icon).
3. Modify the content in the **HTML editor**.

The editor includes:
- Standard formatting (bold, italic, headings, lists, tables)
- **Source code view** — click `<>` to edit the raw HTML if you need fine control
- **Collaborative editing** — multiple users can edit the same page at the same time (changes are merged in real time)

4. Update the **Revision Name** and **Summary** to describe what you changed.
5. Click **Save**.

> **Tip:** The Revision Name and Summary are **required**. Think of them as a mini commit message — they appear in the history log so other people know what changed and why.

### 2.4 Viewing Page History and Revisions

Every time you save a content page, Odoo creates a new **history record**. The current live version is always the most recent one (the **HEAD**).

**To view the history of a page:**

1. Open the page in form view.
2. Go to the **History** tab.
3. You will see a list of all versions with:
   - **ID** — sequential number
   - **Date** — when it was saved
   - **Revision** — the name you gave it
   - **Summary** — what changed
   - **Author** — who saved it

**To compare two versions:**

1. In the History list, click on any row to open it.
2. Switch to the **Changes** tab. This shows a visual diff (green = added, red = removed) between the selected version and the one immediately before it.

You can also browse all history across every page at **Knowledge → Pages → Pages history** (visible to administrators only).

### 2.5 Linking Pages Together (References)

Pages can reference each other so the wiki feels like a true web. The **document_page_reference** module provides two mechanisms:

#### a) Inline references `{{reference_code}}`

Type `{{my_page_reference}}` directly in the HTML editor. The system will:

- Look up a page whose **Reference** field matches `my_page_reference`
- At save time, replace `{{my_page_reference}}` with a clickable link to that page
- If the page doesn't exist yet, the text is rendered as-is (so you can create forward references)

> **Tip:** References are auto-generated from the page title when you first create a page (spaces become underscores). You can override the Reference field manually — it must contain only letters, digits, and underscores, and must be unique.

#### b) Manual links with `oe_direct_line` class

You can also insert an `<a>` tag with `class="oe_direct_line"` and a `name` attribute matching a reference. The parser resolves these the same way.

**To use references effectively:**

1. Open any content page.
2. Look for the **Reference** field near the title (e.g. `onboarding_guide`).
3. On another page, type `{{onboarding_guide}}` in the editor.
4. Save — the placeholder becomes a live link.

> **Note:** In the form view you see two content areas: the raw editor (edit mode) and the parsed view (read mode) where references are resolved. This is by design.

### 2.6 Tagging Pages

Tags are lightweight keywords that help you find and group pages across categories.

**To add tags:**

1. Open a page in form view.
2. In the **Information** tab, find the **Keywords** field.
3. Type to search existing tags or create a new one (press Enter).
4. Tags are colour-coded — each tag has a configurable colour.

**To manage all tags:**

Go to **Knowledge → Configuration → Tags**. From here you can create, rename, recolour, or archive tags.

**To find pages by tag:**

1. Go to **Knowledge → Pages → Pages**.
2. Use the **Tags** filter in the search bar.
3. The search panel on the left also shows tags with counters.

---

## 3. Documents (Attachments)

The Documents area gives you a central place to manage all file attachments in the system. It shows **every attachment** across all Odoo models (invoices, product images, project files, etc.), with special Knowledge-specific fields.

### 3.1 Uploading Files

**To upload a new document:**

1. Go to **Knowledge → Documents → Documents**.
2. Click **New**.
3. Upload your file by clicking the **Upload** button.
4. Fill in:
   - **Name** — a friendly label (auto-filled from the file name)
   - **Folder** — pick a wiki category to file it under (see 3.2)
   - **Related Document** (optional) — link to a specific record in any model
5. Click **Save**.

> **Tip:** Drag and drop files directly onto the Kanban view to upload them instantly.

### 3.2 Organizing Files into Folders

Every document can be assigned to a **Folder**. Folders are **wiki categories** (`document.page` with `type = "category"`).

- The Folder dropdown lists all existing categories.
- You can only pick categories (not content pages).
- To create a new folder on the fly, first create a Category page under **Knowledge → Pages → Categories**.

This means your document filing system is the **same tree** as your wiki table of contents. If you have a category called "Employee Handbook" with child categories "Policies" and "Benefits", you can file documents into any of those three levels.

### 3.3 Viewing Documents

The Documents screen offers three views:

| View | Best for |
|---|---|
| **Kanban** | Visual overview — each card shows the file name, folder badge, and a thumbnail (for images). |
| **List** | A spreadsheet-like table with columns: Name, Folder, Model, File Size, Date. |
| **Form** | Full detail — file metadata, folder, related record link, and download button. |

Switch views using the icons in the top-right corner of the list view.

### 3.4 Searching and Filtering Documents

The search bar lets you find files quickly:

- **Folder** — filter by a specific wiki category
- **Model** — filter by the Odoo model the attachment belongs to (e.g. `sale.order`, `project.task`)
- **Content** — full-text search inside file contents (for text-based files)
- **Name** — search by filename

The search panel on the left shows **Folders** with counters so you can see how many documents are in each folder at a glance.

There is also a built-in **Documents** filter that hides system attachments (like email templates or views) and shows only user-facing files.

> **Tip:** Use the **Favorites** feature to save common searches. For example, save a filter for "Folder = Invoices AND Model = account.move" to get back to it quickly.

### 3.5 Grouping Documents

Grouping lets you pivot your document list. Click **Group By** and choose:

| Group | Result |
|---|---|
| **Folder** | All documents grouped under their wiki category hierarchy. |
| **Model** | Grouped by the Odoo model they belong to (e.g. all Sale Order attachments together). |

Grouping by **Folder** is especially useful because it mirrors your folder structure directly in the list view.

> **Tip:** The default document list already includes the "Group by Folder" toggle in the search bar context. If you don't see it, click **Group By → Folder**.

### 3.6 Previewing Attachments

Click on any document card or row to open the form view. From there:

- **Image preview** — images are shown inline at the top of the form.
- **Download** — click the download button to save the file locally.
- For supported file types, Odoo shows a preview directly in the browser.

A separate **Attachment Preview** module adds a dedicated preview widget for common formats.

### 3.7 Downloading Multiple Files as ZIP

1. Go to **Knowledge → Documents → Documents**.
2. Select the files you want (check the boxes in list view).
3. Click the **Action** (gear) icon and choose **Download**.
4. The browser downloads a single `.zip` file containing all selected documents.

> **Note:** This action is available from the list (tree) view only. It uses the `attachment_zipped_download` module.

---

## 4. Access Control

### 4.1 Page Access Groups

The Knowledge module defines three built-in security groups (under the **Knowledge** application category):

| Group | Permissions |
|---|---|
| **Document Knowledge user** | Base user — can view pages and documents they have access to. |
| **Editor** | Can create and edit wiki pages. |
| **Manager** | Full access to all pages, categories, security settings, and approval workflows. |

Assign these under **Settings → Users & Companies → Users** by editing a user's **Knowledge** application rights.

### 4.2 User / Group Permissions

You can restrict visibility of individual pages and categories with fine-grained rules.

#### a) Visibility groups (simple group-based restriction)

Enabled by the `document_page_group` module:

1. Open a **Category** page.
2. Find the **Visible to** field.
3. Add one or more security groups.
4. Only users in those groups (or their parent groups) will see this category and any content pages inside it.

If no group is set, the category is visible to everyone with Knowledge access. Permissions cascade down — a child category inherits the groups of its parent.

#### b) Direct user / group access (mutually exclusive)

Enabled by the `document_page_access_group` module:

1. Open any **Content** or **Category** page.
2. Go to the **Security** tab (only visible to Managers).
3. You have two mutually exclusive options:
   - **Groups** — select one or more Odoo security groups
   - **Users** — select specific individual users

> **Important:** You cannot set both Groups and Users on the same page. Choose one approach per page.

The system's record rule ensures:
- If Groups are set → only members of those groups can see the page.
- If Users are set → only those specific users can see the page.
- If neither is set → the page is visible to all Knowledge users (subject to the multi-company rule).

#### c) Role-based access (advanced)

If you have the `document_page_access_group_user_role` module, you can also assign **Roles** (from the `res.users.role` model) on the Security tab. Users assigned to those roles automatically get access.

#### d) Approval workflow

The `document_page_approval` module adds an optional approval gate:

1. On a **Category** form, check **Require approval**.
2. Choose an **Approver group**.
3. All child content pages inherit this setting.
4. When a user edits a page that requires approval, the change is saved as a **draft** history record.
5. The user (or an approver) must **Send to Review**, then an approver must **Approve** the change before it becomes the live HEAD version.
6. A **Change Requests** button appears on approved pages so you can manage pending changes.

---

## 5. Best Practices

**Plan your category tree first.** Before writing pages or uploading files, sketch out your categories. A deep but well-organised tree (3–4 levels) is easier to navigate than a flat list of 100 categories.

**Use Templates on categories.** If every page in a category should start with the same structure (e.g. a standard operating procedure template), write it in the category's **Template** field. Every new content page in that category will pre-load it.

**Name revisions meaningfully.** Instead of "Rev 01", use "Added pricing section" or "Fixed broken link to policy". The summary is what people scan in the history list.

**Use references, not manual links.** When you need to point to another wiki page, use `{{reference}}` syntax rather than pasting a URL. If the target page moves, the reference still works.

**Keep documents in folders.** Every uploaded file should have a **Folder** assigned. This makes grouping and searching reliable. A file without a folder can still be found by search but won't appear in folder-based navigation.

**Audit access early.** Before rolling out Knowledge widely, test your permission rules with a non-admin user. It's easy to accidentally hide a category from people who need it.

---

## 6. Common Tasks

### "I want to write a new policy document"

1. Go to **Knowledge → Pages → Categories** and check if a suitable category exists. If not, create one.
2. Go to **Knowledge → Pages → Pages**, click **New**.
3. Enter a Title, select the Category, type "Rev 01" and a summary.
4. Write the policy content. Use `{{related_page_ref}}` to link to other policies.
5. Add relevant Tags in the Keywords field.
6. Click **Save**.

### "I need to upload this quarter's financial report"

1. Go to **Knowledge → Documents → Documents**, click **New**.
2. Upload the PDF.
3. Set the **Folder** to "Finance / Quarterly Reports".
4. Optionally set the **Related Document** to the relevant Accounting record.
5. Click **Save**.

### "I want to see all documents in the HR folder"

1. Go to **Knowledge → Documents → Documents**.
2. In the search panel on the left, click on the "HR" folder.
3. Alternatively, use the search bar → filter by **Folder** → "HR".

### "I accidentally broke a page and need the old version"

1. Open the page, go to the **History** tab.
2. Find the last good version.
3. Open it and copy the content.
4. Go back to the page form, paste the old content into the HTML editor.
5. Give it a revision name like "Restored from version #3" and save.

### "I want to hide a draft category from everyone except the management team"

1. Open the Category page.
2. In the **Visible to** field, add the group "Administration / Manager".
3. Only managers will see it and its child pages.

### "How do I let a contractor see only one specific page?"

1. Open the page.
2. Go to the **Security** tab (you must be a Manager).
3. Under **Users**, add the contractor's user record.
4. Leave all other fields empty. Only that user will see the page.
