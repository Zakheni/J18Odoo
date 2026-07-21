# Zakheni Asset Management — User Guide

**Module:** `zakheni_asset_management`  
**Odoo Version:** 18.0  
**Document Version:** 1.0  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Key Concepts & Data Model](#2-key-concepts--data-model)
3. [Getting Started](#3-getting-started)
4. [Creating & Registering Assets](#4-creating--registering-assets)
5. [Depreciation Schedules](#5-depreciation-schedules)
6. [Asset Assignments to Employees](#6-asset-assignments-to-employees)
7. [Maintenance Tracking](#7-maintenance-tracking)
8. [Barcode / QR Code Labels](#8-barcode--qr-code-labels)
9. [Reporting & Asset Register](#9-reporting--asset-register)
10. [Appendix — Field Reference](#10-appendix--field-reference)

---

## 1. Overview

The **Zakheni Asset Management** module extends Odoo’s standard accounting (Assets) and maintenance applications to provide a complete **asset lifecycle management** solution tailored for the Zakheni group.

### 1.1 What is an Asset?

An *asset* is any tangible item your organisation owns or leases that has value over more than one year — for example:

- Computer hardware (laptops, servers, printers)
- Office furniture and fittings
- Vehicles
- Machinery and production equipment
- Leasehold improvements
- Intangible assets (software licences, patents) — *supported via a separate classification*

### 1.2 Lifecycle Stages

```
 Acquisition / Purchase
        │
        ▼
  Registration & Tagging
        │
        ▼
   In Service / Assigned
        │
        ├──► Maintenance Events
        ├──► Depreciation Runs
        ├──► Employee Transfers
        │
        ▼
  Retirement / Disposal / Sale
```

The module tracks every stage and keeps a full audit trail of movements, value changes, and maintenance history.

### 1.3 Integration Points

| Odoo App | Purpose |
|----------|---------|
| Accounting | Asset financials, depreciation entries, journal items |
| HR / Employees | Assign assets to employees |
| Maintenance | Schedule and log repairs and inspections |
| Inventory / Barcode | QR/barcode label generation and scanning |
| Purchasing | Record purchase cost, vendor, invoice |
| Reporting | Odoo’s pivot/view builder + dedicated asset register |

---

## 2. Key Concepts & Data Model

Before you start, familiarise yourself with the following concepts.

### 2.1 Asset Categories

Categories group assets by type and set **default values**:

- Depreciation method (Straight Line, Declining Balance, etc.)
- Useful life (years or months)
- Account mapping (asset, depreciation, expense)
- Maintenance interval defaults

> **Tip:**  Spend time configuring categories *before* entering assets. Changing the category on an existing asset does **not** retroactively change depreciation entries.

### 2.2 Asset Statuses

Each asset moves through these statuses:

| Status | Meaning |
|--------|---------|
| **Draft** | Newly created; no accounting impact. |
| **In Service** | Asset is active; depreciation can run. |
| **Assigned** | Checked out to an employee. |
| **Under Repair** | Maintenance in progress; usually temporarily unavailable. |
| **Sold** | Fully disposed via sale. |
| ** scrapped** | Dismantled / written off. |

### 2.3 Depreciation Methods

| Method | Description |
|--------|-------------|
| Straight Line (SL) | Equal amount each period over useful life. |
| Declining Balance (DB) | Fixed percentage of remaining book value. |
| Sum-of-Years Digits (SYD) | Accelerated method. |
| Custom Table | Manually enter per-period amounts. |

---

## 3. Getting Started

### 3.1 Enable the App

1. Go to **Apps** → search `zakheni_asset_management`.
2. Click **Activate** (you may need a system administrator to install it).
3. You will see a new top-level menu **Assets** in the main navigation bar.

### 3.2 Configure Basic Settings

Navigate to **Assets → Configuration → Settings**.

- **Default Depreciation Method** — applied when creating a new asset category.
- **Number of years in useful life** — default for new categories.
- **Barcode / QR prefix** — e.g. `ZKA-`.
- **Allow negative book value** — tick if you ever sell assets above book value.

Click **Save**.

### 3.3 Create Asset Categories (Mandatory First Step)

1. Go to **Assets → Configuration → Asset Categories**.
2. Click **New**.
3. Fill in:
   - **Name** — e.g. `Laptops`
   - **Account Prefix** — optional, for auto-account mapping
   - **Useful Life (years)** — e.g. `3`
   - **Depreciation Method** — `Straight Line`
   - **Journal** — the journal that will post depreciation entries
4. On the **Accounts** tab, set:
   - **Asset Account** — balance sheet account where the asset’s cost sits
   - **Depreciation Account** — contra-asset (accumulated depreciation)
   - **Expense Account** — P&L account for the depreciation charge
5. On the **Maintenance** tab, set:
   - **Default Maintenance Interval (days)** — e.g. `180`
6. **Save**.

> **Tip:**  Once you save a category, the accounts cannot be changed on assets that use this category — create a new category if accounts change.

---

## 4. Creating & Registering Assets

### 4.1 Manual Creation

1. **Assets → Assets** → **Create**.
2. On the **General** tab:
   - **Asset Name** — descriptive label (e.g. `Dell Latitude 5540 - ZKA-0042`)
   - **Category** — pick from the configured list
   - **Serial Number / Tag** — manufacturer’s serial number
   - **Barcode** — system-generated or manual
   - **Status** — defaults to *Draft*
   - **Location** — physical location (optional)
   - **Purchase Date** — defaults to today
   - **In Service Date** — when the asset became usable
3. On the **Financial** tab:
   - **Purchase Value** (cost including shipping / installation)
   - **Residual Value** — estimated scrap value at end of life
   - **Salvage Value** — optional
4. On the **Description** tab: add notes, warranty information, or document links.
5. Click **Save** → the asset is now in *Draft*.

#### Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Ctrl + S` | Save |
| `Ctrl + Enter` | Save & Close |
| `Ctrl + Alt + K` | Generate QR code for current asset |

### 4.2 Asset Registration Workflow

Assets should follow this workflow once saved:

1. **Confirm** — click the **Confirm** button on the asset form.
   - This locks the financial fields and changes status to *In Service*.
   - The system can optionally create a journal entry to capitalise the asset.
2. **Print Tag** — generates a QR/barcode label (see §8).
3. **Assign** — assign to an employee or location (see §6).

> **Tip:**  Use the **Register Multiple Assets** wizard (**Assets → Register Multiple Assets**) to bulk-create assets from a CSV or by filling in a table — useful for a batch of identical laptops.

### 4.3 Importing Assets from Spreadsheet

1. **Assets → Assets** → **Favorites** (gear icon) → **Import**.
2. Download the CSV template.
3. Map columns:
   - `name`, `category_id/id`, `purchase_value`, `purchase_date`, `serial_no`, `barcode`
4. Upload the file and click **Import**.
5. Review imported records in draft; confirm them in batches.

---

## 5. Depreciation Schedules

### 5.1 Understanding the Schedule

Every confirmed asset automatically generates a **depreciation schedule** — a table of future depreciation entries.

To view the schedule: open the asset → **Depreciation** tab.

The table shows for each period:

| Period | Date | Amount | Accumulated Depreciation | Book Value | Posted? |
|--------|------|--------|--------------------------|------------|---------|
| 1 | 2026-01-31 | $250.00 | $250.00 | $2,750.00 | ✓ |
| 2 | 2026-02-28 | $250.00 | $500.00 | $2,500.00 | ✓ |
| … | … | … | … | … | … |
| 12 | 2026-12-31 | $250.00 | $3,000.00 | $0.00 | ✓ |

The **book value** column is calculated as:  
    `Book Value = Purchase Value − Accumulated Depreciation − Residual Value`

### 5.2 Modifying a Schedule

Before any depreciation entries are posted:

1. Open the asset → **Depreciation** tab.
2. Click **Edit**.
3. You can:
   - Adjust the number of **Depreciation Lines**
   - Change the **First Depreciation Date**
   - Edit individual line **Amounts**
4. Click **Save**.

> **⚠ Important:**  Once a depreciation entry has been posted (green checkmark), you can no longer edit that line. To correct a posted entry, you must **reverse** the journal entry in Accounting.

### 5.3 Running Depreciation

1. **Assets → Depreciation → Compute Depreciation**.
2. A wizard appears:
   - **Date Range** — select the period end date (e.g. month-end).
   - **Journal** — confirm the posting journal.
3. Click **Compute**.
4. The system creates draft journal entries for each asset due for depreciation.
5. Review them in **Assets → Depreciation → Depreciation Entries**.
6. **Post** the entries to finalise.

> **Tip:**  Schedule this as a recurring action using **Settings → Technical → Scheduled Actions → "Asset Depreciation"** to auto-run every month-end.

### 5.4 Partial / Early Disposal

If you sell or scrap an asset before the end of its useful life:

1. Open the asset → **Disposal** button.
2. Choose **Disposal Method**:
   - *Sale* — enter sale value and customer
   - *Scrap* — write off remaining book value
3. Enter the **Disposal Date**.
4. Click **Dispose**.
5. The system posts a disposal journal entry that:
   - Debits accumulated depreciation (full)
   - Credits the asset account (full)
   - Recognises gain / loss in the P&L

---

## 6. Asset Assignments to Employees

### 6.1 Assigning an Asset

1. Open the asset record.
2. Click the **Assign** button in the header.
3. In the wizard, choose:
   - **Employee** — pick from the HR employee list
   - **Assignment Date** — defaults to today
   - **Expected Return Date** — optional
   - **Notes** — e.g. purpose of assignment
4. Click **Assign**.
5. The asset status changes to *Assigned* and an assignment record appears in the **History** tab.

### 6.2 The Assignment History Tab

Each asset’s **History** tab shows a timeline:

| Date | Employee | Checked Out By | Expected Return | Actual Return |
|------|----------|----------------|----------------|---------------|
| 2026-03-01 | Thabo Nkosi | Admin User | 2026-09-01 | |
| 2025-11-15 | Lindiwe Mthembu | Admin User | | 2026-02-28 |

### 6.3 Returning an Asset

1. Open the asset → **Return** button.
2. Verify the condition of the asset.
3. Enter **Actual Return Date** and any notes (e.g. "Damaged keyboard").
4. Click **Return**.
5. Status reverts to *In Service*.

### 6.4 Transfer between Employees

Two methods:

**Method A — Return + Re-assign** (recommended for audit trail)

1. Click **Return** for the current employee.
2. Click **Assign** for the new employee.

**Method B — Direct Transfer**

1. Click the **Transfer** button.
2. Select the new employee and transfer date.
3. The system automatically returns from the old employee and assigns to the new employee in one step.

### 6.5 Reports by Employee

Go to **Assets → Reporting → Assets by Employee**.

This pivot table shows:
- Employee name
- Assets currently assigned
- Total purchase value assigned
- Count of assets

Export to Excel for sign-off sheets.

---

## 7. Maintenance Tracking

### 7.1 One-off Maintenance Request

1. **Assets → Maintenance → Maintenance Requests** → **Create**.
2. Fill in:
   - **Asset** — link to the asset
   - **Request Date** — today
   - **Description** — e.g. "Replace battery"
   - **Priority** — Low / Medium / High / Critical
   - **Maintenance Type** — Corrective / Preventive
   - **Responsible** — technician
   - **Cost (estimated)** — labour + parts estimate
3. Click **Save**.
4. The request appears in the **Maintenance** tab of the related asset.

### 7.2 Scheduled / Preventive Maintenance

1. **Assets → Configuration → Maintenance Plans** → **Create**.
2. Define:
   - **Plan Name** — e.g. "Quarterly Laptop Check"
   - **Asset** — may leave blank to apply to a category
   - **Asset Category** — filters which assets this plan applies to
   - **Interval** — every `N` days / weeks / months / years
   - **Next Execution Date**
   - **Duration (days)** — expected downtime
3. **Save** → the plan is active.
4. On the trigger date, the system generates a **Maintenance Request** automatically.

> **Tip:**  Use **Asset Categories** to set a default maintenance interval so every asset in that category gets an auto-generated plan upon confirmation.

### 7.3 Asset Downtime Tracking

While a maintenance request is open with status *In Progress*:

- The related asset automatically shows status *Under Repair*.
- The asset cannot be assigned to another employee.
- After the request is set to *Done*, the asset reverts to its previous status.

### 7.4 Maintenance Costs & History

Each maintenance request can track actual costs:

- On the **Costs** tab, enter labour hours, parts, and other expenses.
- The **Total Cost** accumulates on the asset record for reporting.

View full history: open the asset → **Maintenance** tab.

---

## 8. Barcode / QR Code Labels

### 8.1 Generating Labels

The module integrates with Odoo’s label printing to produce **QR code** and **barcode** labels.

**Option A — Single label**

1. Open an asset record.
2. Click **Print → Asset Label (QR)** or **Asset Label (Barcode)**.
3. A PDF / ZPL label is generated with:
   - Company logo
   - Asset name
   - Barcode / QR code encoding the asset ID
   - Serial number
   - Purchase date

**Option B — Batch labels**

1. Go to **Assets → Assets** (list view).
2. Select multiple assets via checkboxes.
3. **Action → Print Labels**.
4. Choose label format (QR / Barcode / Both).
5. Click **Print**.

### 8.2 Label Templates

Navigate to **Assets → Configuration → Label Templates** to customise:

- Paper size (A4, A5, 50×30 mm, etc.)
- Fields shown (name, barcode, category, date)
- Logo position
- Font size

Manage templates per product category if needed.

### 8.3 Scanning in the Field

Use the **Zakheni Mobile** app or a standard barcode scanner:

1. Open **Assets → Scan (mobile view)**.
2. Point your device camera at the QR code.
3. The asset record opens.
4. Actions available on mobile:
   - View details
   - Assign / return
   - Log maintenance
   - Take photo (condition inspection)

### 8.4 Bulk Inventory via CSV Export / Import

1. **Assets → Assets** → **Export** → export barcode / ID / location list.
2. Walk the floor, scan, and record location/condition in the spreadsheet.
3. **Import** the updated file back.

---

## 9. Reporting & Asset Register

### 9.1 Standard Reports

| Report | Location | Description |
|--------|----------|-------------|
| **Asset Register** | Assets → Reporting → Asset Register | Full list with values, depreciation, current status. |
| **Depreciation Forecast** | Assets → Reporting → Depreciation Forecast | Future-period depreciation amounts for budgeting. |
| **Asset History** | Assets → Reporting → Asset History | Movement timeline — assignments, maintenance, disposals. |
| **Assets by Employee** | Assets → Reporting → Assets by Employee | Pivot view of current assignments. |
| **Maintenance Overview** | Assets → Reporting → Maintenance Overview | Open / overdue / completed maintenance requests. |

### 9.2 The Asset Register Report (PDF / Excel)

**To generate:**

1. **Assets → Reporting → Asset Register**.
2. Filter by:
   - Category
   - Status
   - Location
   - Date range (purchase date)
3. Click **Print** or **Export**.

**Columns included (configurable):**

| Column | Description |
|--------|-------------|
| Tag / Barcode | Unique asset identifier |
| Asset Name | Description |
| Category | Laptops, Furniture, etc. |
| Serial Number | Manufacturer serial |
| Purchase Date | Acquisition date |
| Purchase Value | Original cost |
| Accumulated Depreciation | Total depreciation posted to date |
| Current Book Value | Net book value |
| Status | In Service, Assigned, etc. |
| Assigned To | Current employee (if any) |
| Location | Physical location |

> **Tip:**  The **Asset Register** can be scheduled as an automated email via **Reporting → Scheduled Reports** — e.g. send to the CFO every month-end.

### 9.3 Pivot & Graph Views

The **Assets** list view has built-in pivot and graph views:

- **Pivot** — drag fields (Category, Status, Location) into rows/columns; measure sums of Purchase Value or count.
- **Graph** — bar chart of depreciation by category, pie chart of asset statuses, etc.

### 9.4 Excel Export for External Audit

1. Go to any asset list view.
2. **Favorites → Export All**.
3. Choose fields (Barcode, Name, Category, Purchase Value, Book Value, Status, Assigned To).
4. Click **Export** → XLSX.

---

## 10. Appendix — Field Reference

### Asset Form — Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Asset description / label |
| `category_id` | Many2one | Asset category |
| `serial_no` | Char | Manufacturer serial number |
| `barcode` | Char | Unique barcode / QR string |
| `status` | Selection | draft / in_service / assigned / under_repair / sold / scrapped |
| `purchase_date` | Date | Acquisition date |
| `in_service_date` | Date | When placed into service |
| `purchase_value` | Monetary | Original purchase cost |
| `residual_value` | Monetary | Estimated scrap value |
| `salvage_value` | Monetary | Estimated salvage value |
| `book_value` | Monetary | Computed = purchase_value - accumulated_depreciation - residual_value |
| `current_employee_id` | Many2one | Currently assigned employee (read-only) |
| `location` | Char | Physical location |
| `notes` | Text | Internal notes |
| `company_id` | Many2one | Company (multi-company support) |

### Depreciation Line Fields

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | Many2one | Parent asset |
| `date` | Date | Depreciation date |
| `amount` | Monetary | Depreciation amount for this period |
| `accumulated` | Monetary | Running total (computed) |
| `book_value` | Monetary | Book value after this period (computed) |
| `move_id` | Many2one | Journal entry (posted / draft) |
| `type` | Selection | depreciation / disposal / reversal |

---

## Quick Reference — Common Workflows

| Task | Menu Path |
|------|-----------|
| Create a new asset | Assets → Assets → Create |
| Confirm / activate an asset | Open asset → **Confirm** button |
| Assign to employee | Open asset → **Assign** button |
| Return from employee | Open asset → **Return** button |
| Transfer between employees | Open asset → **Transfer** button |
| Run monthly depreciation | Assets → Depreciation → Compute Depreciation |
| Dispose / sell an asset | Open asset → **Disposal** button |
| Log a maintenance request | Assets → Maintenance → Maintenance Requests → Create |
| Print a single asset label | Open asset → Print → Asset Label (QR) |
| Print labels in batch | Asset list → select → Action → Print Labels |
| Run the asset register report | Assets → Reporting → Asset Register |
| Export to Excel | Asset list → Favorites → Export All |

---

*End of document — v1.0*
