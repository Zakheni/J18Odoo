# Contracts User Guide
## Recurring Contracts Management in Odoo 18 (OCA Contract Module)

---

**Document Version:** 1.0  
**Module:** OCA contract (contract)  
**Applies to:** Odoo 18 Enterprise & Community  

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites & Configuration](#prerequisites--configuration)
3. [Creating a Contract](#creating-a-contract)
4. [Contract Lines & Quantities](#contract-lines--quantities)
5. [Variable Quantity Contracts](#variable-quantity-contracts)
6. [Price Revisions](#price-revisions)
7. [Automatic Invoice Generation](#automatic-invoice-generation)
8. [Contract Termination](#contract-termination)
9. [Reporting](#reporting)

---

## Overview

The **OCA Contract** module extends Odoo's standard recurring invoice functionality into a full-featured contract management system. It allows you to:

- Create sales/purchase contracts with recurring invoicing schedules
- Manage contract lines with fixed or variable quantities
- Automate price revisions
- Generate invoices automatically based on contract terms
- Track contract lifecycles from activation to termination
- Analyse contract performance with dedicated reports

---

## Prerequisites & Configuration

### Required Modules

| Module | Technical Name | Purpose |
|--------|---------------|---------|
| Contract | contract | Core recurring contracts engine |
| Contract Sale | contract_sale | Link contracts to sale orders |
| Contract Price Revision | contract_price_revision | Automated price updates |

### Configuration Steps

1. **Activate the Contract module**
   - Navigate to **Apps** → search for **Contract**
   - Install the `Contract` module and any desired sub-modules

2. **Configure Contract Settings**
   - Go to **Contracts** → **Configuration** → **Settings**
   - Set default **Invoice Method**:
     - `Pre-paid`: Invoice at the start of each period
     - `Post-paid`: Invoice at the end of each period
   - Define **Recurring Rules** (monthly, quarterly, yearly, etc.)

3. **Set up User Permissions**
   - Go to **Settings** → **Users & Companies** → **Users**
   - Assign the group **Contract / User** for standard access
   - Assign **Contract / Manager** for full configuration access

> **Tip:** Always test your recurring rules on a sample contract before rolling out to production contracts.

---

## Creating a Contract

### Step-by-Step: New Contract

1. Navigate to **Contracts** → **Contracts** → **Create**

2. Fill in the **Contract Header**:

   | Field | Description | Required |
   |-------|-------------|----------|
   | **Name** | Contract reference/title | Yes |
   | **Partner** | Customer or vendor | Yes |
   | **Contract Template** | Pre-defined template (optional) | No |
   | **Responsible** | Salesperson or account manager | Recommended |
   | **Company** | Company (multi-company setups) | Yes |
   | **Currency** | Invoicing currency | Yes |

3. Define **Invoicing Schedule**:

   | Field | Description |
   |-------|-------------|
   | **Contract Type** | `Sales` or `Purchases` |
   | **Recurring Next Date** | First invoice date |
   | **Recurring Rule** | `Monthly`, `Quarterly`, `Yearly`, or `Custom` |
   | **Interval** | `1` (every month), `3` (every 3 months), etc. |
   | **Recurring Invoice Method** | `Pre-paid` or `Post-paid` |

4. Set **Contract Dates**:

   | Field | Description |
   |-------|-------------|
   | **Start Date** | When the contract becomes active |
   | **End Date** | When the contract expires (leave empty for indefinite) |

5. Click **Save**

> **Tip:** Use **Contract Templates** to pre-fill common terms, lines, and schedules. Define them at *Contracts → Configuration → Contract Templates*.

### Contract States

| State | Meaning |
|-------|---------|
| **Draft** | Not yet confirmed; editable |
| **Confirmed** | Active and generating invoices |
| **Terminated** | Manually ended; no further invoices |
| **Cancelled** | Voided; no effect |

---

## Contract Lines & Quantities

### Adding Contract Lines

Contract lines define the products/services billed under the contract.

1. Open a contract and switch to the **Contract Lines** tab
2. Click **Add a line**
3. Fill in:

   | Field | Description |
   |-------|-------------|
   | **Product** | The product/service to bill |
   | **Name** | Description (auto-filled from product) |
   | **Quantity** | Number of units per period |
   | **Unit Price** | Price per unit |
   | **Recurring Next Date** | Override for this specific line (optional) |
   | **Recurring Rule** | Override for this specific line (optional) |
   | **Analytic Account** | For cost/profitability tracking |

4. The **Subtotal** is calculated automatically as `Qty × Unit Price`

### Editing Quantities Mid-Contract

- You can modify the **Quantity** field at any time
- The change takes effect from the **next invoice run**
- Past invoices are **not retroactively adjusted**

### Recurring Invoicing Grouping

Lines with the same **Recurring Next Date** and **Recurring Rule** are grouped into a single invoice. Different dates/rules produce separate invoices.

> **Tip:** Use separate contract lines for services billed at different frequencies (e.g., monthly support + quarterly consulting).

---

## Variable Quantity Contracts

Variable quantity contracts are ideal when usage fluctuates each period (e.g., pay-per-user SaaS, consumption-based billing).

### Configuring Variable Quantity

1. On the **product** form (in *Sales → Products*), ensure the product is correctly set up as a service or consumable

2. On the **Contract Line**, set the **Quantity** to a default starting value

3. Enable **Variable Quantity** on the contract line by checking the box (this field appears when the OCA module `contract_variable_quantity` is installed)

4. Set the **Variable Quantity Method**:

   | Method | Description |
   |--------|-------------|
   | **Manual** | User enters quantity each period before invoicing |
   | **Previous Period Usage** | Auto-calculated from the last period's consumption |

### Using Manual Variable Quantity

1. Before each invoice run, navigate to **Contracts** → **Variable Quantities**
2. You will see a list of pending variable quantity lines awaiting entry
3. Enter the **Actual Quantity** for the current period
4. Save — the invoice will pick up this updated quantity

### Using Automated Variable Quantity

When linked to a sale order or timesheet, the system can:
- Count the number of users/units active during the period
- Aggregate timesheet hours logged
- Sum quantities from linked pickings

### Generating a Mid-Period Invoice

1. Go to the contract line
2. Click **Manual Invoice**
3. The system prorates the quantity based on days elapsed
4. Review and validate

> **Tip:** Set email reminders for variable quantity entry — go to *Contracts → Configuration → Scheduled Actions* and enable the "Variable Quantity Reminder" job.

---

## Price Revisions

The **Contract Price Revision** module automates price updates based on indexes, dates, or percentages.

### Activating Price Revision

1. Install the module `contract_price_revision`
2. Go to **Contracts** → **Configuration** → **Price Revision Config**

### Configuring a Price Revision Rule

1. Create a new **Price Revision Config**
2. Define:

   | Field | Description |
   |-------|-------------|
   | **Name** | Internal rule name |
   | **Price Revision Method** | See table below |
   | **Percent** | Percentage to apply (for percentage method) |
   | **Limit** | Minimum/maximum increase cap |

3. Link the rule to specific contracts or contract lines

### Price Revision Methods

| Method | Behaviour |
|--------|-----------|
| **Fixed Percentage** | Increases/decreases price by X% on each revision date |
| **On Index** | Adjusts price based on a published index (e.g., CPI) |
| **On Date** | Applies a one-time price change on a specific date |
| **From Previous Price** | Uses the last invoice price as the base |

### Applying a Price Revision

1. When the revision date arrives, a **Price Revision** record is created
2. Go to **Contracts** → **Price Revisions** → **Pending Revisions**
3. Review each pending revision
4. Click **Apply** to update the contract line price
5. The new price takes effect on the next invoice

> **Tip:** Create a **Cron Job** to auto-apply price revisions. Go to *Settings → Technical → Scheduled Actions → Apply Contract Price Revisions* and set it to `Hourly` or `Daily`.

### Manual Price Override

- You can also manually edit the **Unit Price** field on any contract line at any time
- Future invoices use the new price
- No price revision record is created (no audit trail — use with caution)

---

## Automatic Invoice Generation

### How Auto-Invoicing Works

The system checks daily for contracts whose **Recurring Next Date** has been reached and generates invoices automatically.

### Triggering Auto-Invoice

**Method 1 — Scheduled Action (Automatic):**
1. Go to **Settings** → **Technical** → **Scheduled Actions**
2. Locate **Contract: Recurring - Invoice**
3. Set the action to **Active**
4. Configure frequency (daily recommended)

**Method 2 — Manual Trigger:**
1. Go to **Contracts** → **Contracts**
2. Select the contract(s) to invoice
3. Click **Action** → **Create Invoice**
4. System generates draft invoices

### What Happens During Invoice Generation

For each contract line due:
1. An **invoice line** is created with:
   - Product, description, quantity, unit price, subtotal
   - Analytic account from the contract line
   - Taxes from the product
2. The invoice is set to **Draft** status
3. The contract's **Recurring Next Date** advances by the recurring interval

### Post-Generation Steps

1. Go to **Invoicing** → **Customers** → **Invoices**
2. Filter by status **Draft**
3. Review each invoice
4. Click **Validate** (or use **Action** → **Validate Invoices** for batch)
5. Send to customer via **Send & Print**

### Prorating

For mid-period changes, the system supports:
- **Start Proration**: First invoice covers from start date to end of first period
- **End Proration**: Final invoice covers from last period start to end date

Proration is calculated as: `(Days in period / Total days in full period) × Full price`

> **Tip:** If an invoice is generated with incorrect quantities, you can **reset to draft**, edit the quantities, and re-validate. The *Recurring Next Date* is not affected by manual edits.

---

## Contract Termination

### Terminating a Contract

1. Open the contract
2. Click **Action** → **Terminate**
3. Enter the **Termination Date**
4. Choose an optional **Termination Reason** (from a configured list)
5. Confirm

### What Termination Does

- Sets the contract state to **Terminated**
- Sets the **End Date** to the termination date
- **Stops all future invoice generation**
- If a final invoice is needed:
  - Click **Create Invoice** before terminating
  - Or set **Termination Date** to align with the last invoiced period

### Early Termination Fees

You can configure an early termination fee:

1. Go to **Contracts** → **Configuration** → **Termination Reasons**
2. Create or edit a reason
3. Set **Early Termination Fee Product**
4. Set **Fee Amount**
5. When terminating with this reason, the fee is automatically added to the final invoice

### Reactivating a Terminated Contract

1. Open the terminated contract
2. Click **Action** → **Set to Draft**
3. Edit dates and terms as needed
4. Click **Confirm**

### Cancelling a Contract (vs Terminating)

| Action | Effect |
|--------|--------|
| **Cancel** | Void contract; no invoices generated or expected |
| **Terminate** | End active contract; final invoice + termination fee possible |

> **Tip:** Configure **Termination Approval** at *Contracts → Configuration → Settings → Require Manager Approval for Termination* to prevent accidental terminations.

---

## Reporting

### Contract Reports

Navigate to **Contracts** → **Reporting**:

| Report | Purpose |
|--------|---------|
| **Contract Analysis** | Aggregate view of all contracts by partner, product, state |
| **Recurring Revenue Forecast** | Projected revenue for future periods |
| **Contract Renewal Analysis** | Contracts ending soon; renewal opportunities |
| **Churn Analysis** | Terminated contracts grouped by reason and period |

### Contract Analysis Pivot

1. Go to **Contracts** → **Reporting** → **Contract Analysis**
2. Use the **Pivot** view to group by:
   - Partner
   - Product
   - State
   - Salesperson
   - Start/End Month
3. Measures include:
   - Number of contracts
   - Total contract value
   - Average contract value
   - Remaining duration

### Recurring Revenue Forecast

This report shows:
- Invoiced revenue per month (historical)
- Expected revenue per month (future)
- Churned/expired contracts and lost revenue

Use it for:
- Board reporting
- Cash flow forecasting
- Sales performance reviews

### Excel Export

1. Open any report/pivot view
2. Click the **gear icon** ⚙ → **Export All**
3. Choose XLSX format
4. Select fields to export
5. Download

> **Tip:** Create **Dashboard Favourites** by setting up a pivot with your preferred dimensions and clicking *Add to Dashboard*. Access it from the Odoo dashboard for one-click reporting.

### Scheduled Report Emails

1. Go to the desired report view
2. Click **Action** → **Send by Email**
3. Configure recipients, frequency, and format (PDF/XLSX)
4. Click **Set Scheduled Report**
5. Reports are automatically emailed on the schedule

---

## Appendix: Key Shortcuts

| Action | Navigation |
|--------|-----------|
| New Contract | Contracts → Contracts → Create |
| Contract Templates | Contracts → Configuration → Templates |
| Pending Invoices | Invoicing → Customers → Invoices (filter: Draft) |
| Price Revisions | Contracts → Price Revisions → Pending |
| Report Dashboard | Contracts → Reporting → Contract Analysis |

---

*End of Document*
