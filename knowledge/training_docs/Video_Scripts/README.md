# Odoo 18 Training Video Scripts

This directory contains video scripts for recording Odoo 18 training content. Use these scripts to create consistent, high-quality training videos for end users and implementation teams.

---

## How to Use These Video Scripts

1. **Choose a module** — each subdirectory contains scripts scoped to a specific Odoo module (CRM, Sales, Inventory, etc.).
2. **Read the script fully** before recording so you understand the flow and can anticipate UI transitions.
3. **Customise the script** — replace generic placeholders like `[COMPANY NAME]` or `[YOUR DATA]` with your own demo environment values.
4. **Record in short takes** — pause between sections. It is easier to edit multiple short clips than one long recording.
5. **Review and re-record** if needed. Do not aim for perfection on the first take.

---

## Recommended Tools

| Tool | Platform | Cost | Notes |
|------|----------|------|-------|
| [OBS Studio](https://obsproject.com/) | Windows, macOS, Linux | Free | Open-source; powerful but requires initial setup. Best for full control. |
| [Camtasia](https://www.techsmith.com/camtasia.html) | Windows, macOS | Paid | Built-in video editor with captions, transitions, and callouts. Great for polish. |
| [Loom](https://www.loom.com/) | Browser, Desktop | Free tier + Paid | Quick recording and sharing. Ideal for short walkthroughs or async feedback. |
| [ScreenPal (formerly Screencast-O-Matic)](https://screenpal.com/) | Windows, macOS | Free tier + Paid | Simple editor, good for beginners. Paid plan removes watermark and adds editing. |

---

## Best Practices for Recording Training Videos

- **Keep videos under 10 minutes.** If a topic needs more time, split it into multiple videos.
- **Plan your script before recording.** Know every click, field entry, and navigation step.
- **Use a clean, quiet environment.** Close email, Slack, and other noisy applications.
- **Speak clearly at a moderate pace.** Pause between sentences. Let the viewer absorb what you just showed.
- **Show cursor movements clearly.** Avoid erratic mouse movements. Use slow, deliberate motions.
- **Add captions and subtitles.** Improves accessibility and helps non-native speakers.
- **Use zoom-in for small UI elements.** Buttons, dropdown arrows, and form fields are often hard to see at full-screen resolution.

---

## Video Naming Convention

Use the following format for all video files:

```
ODO<VER>_<MODULE>_<NNN>_<ShortDescription>.mp4
```

| Part | Example | Notes |
|------|---------|-------|
| Version | `ODO18` | Odoo 18 |
| Module | `CRM` | Uppercase module abbreviation |
| Sequence | `01` | Zero-padded two-digit number |
| Description | `CreatingOpportunities` | PascalCase, no spaces |

**Example:** `ODO18_CRM_01_CreatingOpportunities.mp4`

---

## Suggested Video Series Structure

| Segment | Duration | Content |
|---------|----------|---------|
| **Intro video** | 2–3 min | What the module does, who it is for, what will be covered |
| **Module overview** | 5–7 min | Dashboard, key menus, configuration settings, high-level workflow |
| **Individual topic videos** | 3–10 min each | One feature or process per video (e.g., "Creating a Quote", "Sending Invoices") |
| **Workflow walkthroughs** | 10–15 min | End-to-end scenarios that tie multiple features together |

---

## Template Reference

A reusable script template is available at:

```
Templates/video_script_template.md
```

Copy this file for each new video and fill in the sections. The template includes placeholders for objectives, prerequisites, step-by-step instructions, key takeaways, and review notes.

---

## Example Video List by Module

### CRM

1. `ODO18_CRM_01_CreatingAndManagingOpportunities.mp4` — Creating and Managing Opportunities
2. `ODO18_CRM_02_ConvertingLeadsToCustomers.mp4` — Converting Leads to Customers
3. `ODO18_CRM_03_PipelineAnalysisReports.mp4` — Pipeline Analysis Reports
4. `ODO18_CRM_04_EmailTemplatesAndAutomatedActions.mp4` — Email Templates and Automated Actions

### Sales

1. `ODO18_SALES_01_CreatingCustomerQuotes.mp4` — Creating Customer Quotes
2. `ODO18_SALES_02_OrderConfirmationAndInvoicing.mp4` — Order Confirmation and Invoicing
3. `ODO18_SALES_03_ProductCatalogManagement.mp4` — Product Catalogue Management
4. `ODO18_SALES_04_PricelistsAndDiscounts.mp4` — Pricelists and Discounts

### Inventory

1. `ODO18_INV_01_WarehouseConfiguration.mp4` — Warehouse Configuration
2. `ODO18_INV_02_ReceivingAndPuttingAwayProducts.mp4` — Receiving and Putting Away Products
3. `ODO18_INV_03_StockMovesAndInventoryAdjustments.mp4` — Stock Moves and Inventory Adjustments
4. `ODO18_INV_04_ReorderingRulesAndAutomatedProcurement.mp4` — Reordering Rules and Automated Procurement

### Accounting

1. `ODO18_ACCT_01_ChartOfAccountsSetup.mp4` — Chart of Accounts Setup
2. `ODO18_ACCT_02_CustomerAndVendorInvoices.mp4` — Customer and Vendor Invoices
3. `ODO18_ACCT_03_BankReconciliation.mp4` — Bank Reconciliation
4. `ODO18_ACCT_04_FinancialReportsAndTaxReturns.mp4` — Financial Reports and Tax Returns

### HR

1. `ODO18_HR_01_EmployeeMasterData.mp4` — Employee Master Data
2. `ODO18_HR_02_LeaveManagement.mp4` — Leave Management
3. `ODO18_HR_03_ExpenseReporting.mp4` — Expense Reporting
4. `ODO18_HR_04_RecruitmentProcess.mp4` — Recruitment Process

### Manufacturing

1. `ODO18_MFG_01_BOMAndRoutingSetup.mp4` — Bill of Materials and Routing Setup
2. `ODO18_MFG_02_ProductionOrderLifecycle.mp4` — Production Order Lifecycle
3. `ODO18_MFG_03_WorkCenterAndMOPlanning.mp4` — Work Centre and Manufacturing Order Planning
4. `ODO18_MFG_04_QualityControlChecks.mp4` — Quality Control Checks
