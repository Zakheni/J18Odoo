# Odoo 18 Accounting Module — End-User Manual

> **Target audience:** Accountants, Bookkeepers, Finance teams  
> **Applies to:** Odoo 18 Community & Enterprise  
> **Last updated:** July 2026

---

## Table of Contents

1. [Overview](#1-overview)
2. [Dashboard](#2-dashboard)
3. [Customers (Accounts Receivable)](#3-customers-accounts-receivable)
4. [Vendors (Accounts Payable)](#4-vendors-accounts-payable)
5. [Payments](#5-payments)
6. [Bank Reconciliation](#6-bank-reconciliation)
7. [Charts of Accounts](#7-charts-of-accounts)
8. [Journals](#8-journals)
9. [Taxes](#9-taxes)
10. [Reporting](#10-reporting)
11. [Period End](#11-period-end)
12. [Advanced Features](#12-advanced-features)
13. [SA-Specific (South Africa)](#13-sa-specific-south-africa)
14. [Common Workflows](#14-common-workflows)

---

## 1. Overview

The Accounting module handles the full financial cycle:

| Area | What it does |
|---|---|
| **Customer Invoices** | Bill your customers for goods/services |
| **Vendor Bills** | Record what you owe suppliers |
| **Payments** | Record money in and out |
| **Reconciliation** | Match bank transactions to invoices/bills |
| **Reporting** | P&L, Balance Sheet, Trial Balance, Tax reports |
| **Period End** | Lock dates, fiscal year close |

> **Tip:** In Odoo 18, Accounting is tightly integrated with Sales, Purchasing, Inventory, and Payroll. Most invoices are created automatically from sales orders / purchase orders.

---

## 2. Dashboard

Navigate to **Accounting → Dashboard**.

### 2.1 Key Metrics Cards

At the top of the dashboard you see:

- **Receivable** — total outstanding customer debt
- **Payable** — total outstanding vendor debt
- **Cash/Bank** — current bank & cash balances
- **Net Income (Period)** — profit/loss for the selected period
- **Quick Stats** — number of draft invoices, overdue invoices, unreconciled items

### 2.2 Journal Dashboards

Below the metrics, each journal appears as a card:

```
│ Bank Account (Current) │
│ Balance: R 125 430.00  │
│ [New] [Statements]     │
│ Last Reconciled: 30 Jun│
```

Click a card to open the journal's entries.

### 2.3 Lock Dates

Use lock dates to prevent changes to closed periods:

- **Accounting Lock Date** — prevents changing journal items before this date
- **Invoicing Lock Date** — prevents creating/modifying invoices before this date

Set them via: **Accounting → Configuration → Settings → Lock Dates**.

> **Tip:** Always set the lock date after month/year-end to protect finalized data.

---

## 3. Customers (Accounts Receivable)

### 3.1 Creating a Customer Invoice

1. Go to **Accounting → Customers → Invoices**.
2. Click **New**.
3. **Customer**: select or create a contact.
4. **Invoice Date**: defaults to today; adjust if needed.
5. **Due Date**: auto-calculated from payment terms; override manually.
6. **Journal**: defaults to Customer Invoices (Sales Journal).
7. **Invoice Lines**:
   - **Product**: select a product or enter a description.
   - **Quantity / Unit Price**.
   - **Taxes**: auto-applied from product; override if needed.
8. **Optional tabs**:
   - **Journal Items** — view the debit/credit breakdown.
   - **Payment** — shows due/payment history.
   - **Accounting** — shows analytic distribution.
9. Click **Confirm** to validate (Post) the invoice.
10. Click **Send & Print** to email the PDF to the customer.

> **Tip:** Invoicing from a sales order? Go to the SO → **Create Invoice** — this copies all lines, quantities, and delivery info automatically.

### 3.2 Credit Notes & Refunds

**Method A — From an existing invoice (recommended):**

1. Open the validated invoice.
2. Click **Add Credit Note**.
3. Choose:
   - **Full Refund** — reverses the entire invoice.
   - **Partial Refund** — lets you modify lines.
4. Choose the credit reason (required for tax compliance).
5. Click **Reverse** → a credit note is created and auto-reconciled with the original invoice.

**Method B — Standalone credit note:**

1. **Accounting → Customers → Credit Notes** → **New**.
2. Fill in customer, lines, and taxes.
3. Click **Confirm**.
4. Use **Payments → Register Payment** to refund if needed.

> **Tip:** Credit notes appear as negative amounts on reports. They reduce the customer's outstanding balance.

### 3.3 Payment Terms

Set up at **Accounting → Configuration → Payment Terms**.

Common terms:

| Term | Meaning |
|---|---|
| Immediate Payment | Due on invoice date |
| 30 Days (Net 30) | Due 30 days after invoice date |
| 2% 10/30 Net 30 | 2% discount if paid within 10 days |
| End of Month (EOM) | Due at month-end |
| End of Following Month | Due end of next month |

> **Tip:** Assign a default payment term on the customer form (Accounting tab). It auto-populates on invoices.

### 3.4 Down Payments

Used for deposits/advance payments.

1. On a sales order, click **Down Payment**.
2. Choose **Fixed amount** or **Percentage**.
3. Odoo creates a draft invoice for the deposit.
4. Confirm and send as usual.

---

## 4. Vendors (Accounts Payable)

### 4.1 Creating a Vendor Bill

1. **Accounting → Vendors → Bills**
2. Click **New**.
3. **Vendor**: select or create.
4. **Bill Date** and **Due Date**.
5. **Journal**: defaults to Vendor Bills (Purchase Journal).
6. **Lines**: product, description, quantity, unit price, taxes.
7. Click **Confirm**.

> **Tip:** When a purchase order is validated (received), you can click **Create Bill** to generate the bill from the PO. For "bill-on-order" products, Odoo creates a draft bill automatically.

### 4.2 Credit Notes from Vendors

1. Open the vendor bill.
2. Click **Add Credit Note**.
3. Choose full or partial reversal.
4. Reason is required.
5. Click **Reverse**.

Or create directly: **Accounting → Vendors → Credit Notes** → **New**.

### 4.3 Payment Tracking

Inside any vendor bill you see:

- **Payment Status**: Not Paid / In Payment / Paid
- **Payment History**: lists every payment applied

> **Tip:** Use the **Vendor Bill Aging** report (Reporting → Aging Reports) to see which bills are overdue.

---

## 5. Payments

### 5.1 Registering a Payment (Customer)

1. Open the invoice.
2. Click **Register Payment**.
3. **Payment Method**: Manual / Check / Electronic / SEPA (varies by country).
4. **Amount**: defaults to the open balance; adjust for partial payments.
5. **Payment Date**: actual date of receipt.
6. **Bank Journal**: select the bank account where money was deposited.
7. **Memo / Reference**: optional.
8. Click **Register Payment**.

The invoice is now marked **In Payment** or **Paid**, and a bank transaction is created.

### 5.2 Registering a Payment (Vendor)

Same flow from a vendor bill → **Register Payment**.

Use **Payment Type = Send** to record outgoing money.

### 5.3 Batch Payments

**Accounting → Payments → Batch Payments** lets you pay multiple bills at once.

1. Create a new batch.
2. Select mode: **Customers (incoming)** or **Vendors (outgoing)**.
3. Add open invoices/bills.
4. Click **Create Payment** → Odoo generates individual payments.
5. Optional: generate a SEPA XML or print a check report.

### 5.4 Payment Methods

Configure at **Accounting → Configuration → Payment Methods**.

Each method links to a **Bank Journal** and has a **Payment Type**:

- **Inbound** — customer pays you (receipts)
- **Outbound** — you pay vendor (payments)

> **Tip:** Payment method codes (e.g. `manual_out`) are used in reports. Keep them descriptive.

### 5.5 Payment Matching (Reconciliation)

When a payment is registered, Odoo automatically reconciles it with the invoice. You can also:

1. **Accounting → Overview** → **Reconciliation** → click the bank journal card.
2. See the payment on one side, the invoice on the other.
3. Click **Validate** to match them.

---

## 6. Bank Reconciliation

### 6.1 Import Bank Statements

1. **Accounting → Overview** → click the bank journal card.
2. Click **Import Statement** (or **New** to enter manually).
3. Supported formats: **CSV**, **OFX**, **QIF**, **CODA** (Belgium), **CAMT.053** (SEPA).
4. Select your file, map columns (date, description, amount, reference).
5. Click **Import** — Odoo creates bank statement lines.

### 6.2 Auto-Reconciliation

Odoo suggests matches based on:

- Amount match
- Reference match
- Partner match
- Label matching

In the statement line view:

1. A suggested match appears in the right panel.
2. Click **Validate** to accept.
3. If no match, click **Create / Add** to manually reconcile.

### 6.3 Manual Reconciliation

1. From the bank journal card, click **Reconciliation**.
2. Select the statement line.
3. In the right panel, search for the invoice/bill or click **New** to create one.
4. Use **Add an item** for non-invoice transactions (bank charges, interest).
5. Click **Validate**.

### 6.4 Write-Offs

For small differences (bank charges, rounding):

1. During reconciliation, click the **Write-Off** button.
2. Choose an **Account** (e.g. Bank Charges, Discount).
3. Enter the **Amount** and **Tax** if applicable.
4. Click **Confirm**.

### 6.5 Bank Reconciliation Model

Save time by setting up rules:

**Accounting → Configuration → Reconciliation Models**.

| Setting | Example |
|---|---|
| Match Text | "ATM FEE" |
| Journal | Bank Account |
| Account | Bank Charges (6120) |
| Label | "Bank Charges" |
| Amount | Fixed or percentage |

When a statement line matches the rule, Odoo auto-reconciles it without human intervention.

### 6.6 Unreconciled Items

**Accounting → Reports → Unreconciled Items** shows all entries not yet matched.

> **Tip:** Run this report before month-end to catch orphan items.

---

## 7. Charts of Accounts

### 7.1 Structure

**Accounting → Configuration → Chart of Accounts**.

Odoo uses a **prefix-based** structure:

| Prefix Range | Account Type | Example |
|---|---|---|
| 1xxx | Assets | 1100 Bank Current |
| 2xxx | Liabilities | 2100 Trade Payables |
| 3xxx | Equity | 3100 Retained Earnings |
| 4xxx | Income | 4100 Sales Revenue |
| 5xxx | Expenses | 5200 Rent |
| 6xxx | Expenses (detail) | 6100 Bank Charges |

> **Tip:** In South Africa, the default CoA uses SARS-compatible codes. You can add new accounts at any time.

### 7.2 Account Types

Each account has a **Type** that determines its behaviour:

| Type | Reports | Behaviour |
|---|---|---|
| Asset | Balance Sheet | Debit increases, Credit decreases |
| Liability | Balance Sheet | Credit increases, Debit decreases |
| Equity | Balance Sheet | Credit increases |
| Income | P&L | Credit increases (revenue) |
| Expense | P&L | Debit increases (costs) |
| Payable | Balance Sheet | Auto recomputed from vendor bills |
| Receivable | Balance Sheet | Auto recomputed from invoices |

### 7.3 Taxes

Taxes are linked to accounts (e.g. VAT Input / VAT Output). Configure:

**Accounting → Configuration → Taxes**.

See [Section 9 — Taxes](#9-taxes) for full details.

---

## 8. Journals

### 8.1 Types of Journals

| Journal Type | Default Use | Example Name |
|---|---|---|
| **Sale** | Customer invoices & credit notes | Customer Invoices |
| **Purchase** | Vendor bills & credit notes | Vendor Bills |
| **Bank & Cash** | Bank statements, payments | Current Account, Petty Cash |
| **General** | Miscellaneous entries | Miscellaneous Operations |
| **Sales (Euro)** | Multi-currency sales | Sales EUR (if enabled) |

### 8.2 Creating Journal Entries

**Accounting → Accounting → Journal Entries** → **New**.

1. **Journal**: select General Journal.
2. **Date**: transaction date.
3. **Lines**:
   - At least one Debit and one Credit line.
   - Account, Label, Debit/Credit, Partner (optional).
4. Click **Post**.

> **Tip:** Use **Auto-Reverse** if this entry needs to reverse next period (e.g. accruals).

### 8.3 Posting

- **Draft entries** — editable, visible only to you.
- **Posted entries** — locked, appear in reports.
- Click **Post** to finalize.

> **Warning:** A posted journal entry cannot be edited. Use **Reverse Journal Entry** to create a reversing entry.

### 8.4 Journal Entry Templates

Reuse common entries:

1. Create a entry normally.
2. Click **Save as Template**.
3. Name it (e.g. "Monthly Depreciation").
4. Apply: **Journal Entries → From Template**.

---

## 9. Taxes

### 9.1 Setting Up Tax Rates

**Accounting → Configuration → Taxes** → **New**.

| Field | Example |
|---|---|
| Name | VAT 15% |
| Tax Type | Sales / Purchase / None |
| Amount | 15.00% |
| Tax Group | VAT (or leave blank) |
| Tax Scope | Goods / Services / All |
| Distribution for Invoices | Account: VAT Output, 100% |
| Distribution for Credit Notes | Account: VAT Output, -100% |

> **Tip:** A **Sales** tax is charged to customers. A **Purchase** tax is reclaimed from government. Use **None** for tax-exclusive prices.

### 9.2 Tax Groups

Group related taxes for reporting (e.g. "VAT 15% + VAT 0% + VAT Exempt").

**Accounting → Configuration → Tax Groups** → **New**.

| Field | Purpose |
|---|---|
| Name | "VAT" |
| Sequence | Determines display order |
| Tax Type | Tax group type (defaults) |

### 9.3 Tax Reports

**Reporting → Audit Reports → Tax Report**.

Select the **Tax Group** and date range. Odoo shows:

- Base Amount (net)
- Tax Amount (VAT)
- Total (gross)

For SARS VAT201 reporting, see [Section 13](#13-sa-specific-south-africa).

### 9.4 Tax Closures

**Accounting → Configuration → Taxes → Tax Closures**.

Closures lock tax periods so no one can change invoices/bills in a past tax period.

> **Tip:** Close each VAT period after filing.

---

## 10. Reporting

All reports are under **Accounting → Reporting**.

### 10.1 Aged Receivable

Shows outstanding customer invoices grouped by aging buckets:

- Current
- 0–30 Days Overdue
- 30–60 Days
- 60–90 Days
- 90+ Days

**How to run:**

1. **Reporting → Aging Reports → Aged Receivable**.
2. Set the **Date at** (report date).
3. Filter by **Customer** if needed.
4. Click **Print** or **Export**.

### 10.2 Aged Payable

Same layout for vendor bills.

**Reporting → Aging Reports → Aged Payable**.

### 10.3 General Ledger

Shows every journal entry for selected accounts.

1. **Reporting → Audit Reports → General Ledger**.
2. Select **Account(s)**, date range, and filters.
3. Columns: Date, Ref, Partner, Debit, Credit, Balance.

### 10.4 Trial Balance

Lists every account with its Debit/Credit totals and net balance.

1. **Reporting → Audit Reports → Trial Balance**.
2. Set date range.
3. **Display Ledger** — expand to see underlying journal items.

### 10.5 Profit & Loss (Income Statement)

**Reporting → Partner Reports → Profit & Loss** (Enterprise) or use **Custom Reports**.

Shows Income - Expenses = Net Profit.

### 10.6 Balance Sheet

**Reporting → Partner Reports → Balance Sheet**.

Assets = Liabilities + Equity.

### 10.7 Exporting Reports

All reports can be:

- **Print (PDF)** — formal layout.
- **Export (XLSX)** — editable Excel.
- **Export (CSV/PDF)** — choose in the dropdown.

> **Tip:** Customize report layouts under **Accounting → Configuration → Reports → Report Templates**.

---

## 11. Period End

### 11.1 Fiscal Year

**Accounting → Configuration → Fiscal Years**.

Each year has:

- **Name** (e.g. "FY 2026")
- **Start / End Date**
- **Status**: Open or Closed

> **Tip:** Keep the current year Open and prior years Closed.

### 11.2 Lock Dates

Set at **Accounting → Settings → Lock Dates**.

| Lock Field | Effect |
|---|---|
| **Invoicing Lock Date** | No invoices/bills can be created/edited before this date |
| **Accounting Lock Date** | No journal entries can be created/edited before this date |
| **Bank Statement Lock Date** | No statement lines can be added before this date |

### 11.3 Period-End Checklist

1. Reconcile all bank accounts.
2. Run Trial Balance — investigate differences.
3. Post all outstanding invoices/bills.
4. Run VAT report and file return.
5. Set lock dates for closed months.
6. If fiscal year-end:
   - Run P&L and Balance Sheet.
   - Post closing entries (retained earnings).
   - Close fiscal year.

> **Tip:** Use **Accounting → Period End Tasks** (Enterprise) to manage a checklist.

### 11.4 Fiscal Year Close

1. Ensure all entries are posted.
2. Transfer Net Income to Retained Earnings:
   - A closing entry is usually automated in Enterprise.
   - In Community, create a manual journal entry.
3. Close the fiscal year:
   **Accounting → Configuration → Fiscal Years** → **Close**.
4. Open the new fiscal year (Odoo creates it automatically).

### 11.5 Reversing Entries

For accruals and prepayments:

1. Create the journal entry with a future date.
2. Tick **Auto-Reverse** → set reversal date.
3. On the reversal date, Odoo creates an opposite entry automatically.

---

## 12. Advanced Features

### 12.1 Deferred Revenue

Recognise income over multiple periods.

1. On the invoice line, click the **Deferral** tab.
2. Tick **Deferred Revenue**.
3. Set **Start Date** and **End Date** (e.g. 1 Jan – 31 Dec for a yearly subscription).
4. Confirm the invoice.
5. Odoo creates a Deferred Revenue account entry and an automated journal entry template.
6. Each month, Odoo posts the monthly portion to the income account.

**Configure:**

- **Deferred Revenue Account**: Balance Sheet liability account.
- **Deferred Revenue Model**: found in **Accounting → Configuration → Deferred Revenue Models**.

### 12.2 Deferred Expenses

Same logic for expenses (prepaid rent, insurance):

1. On the vendor bill line → **Deferral** tab → **Deferred Expense**.
2. Set start/end dates.
3. Odoo amortises monthly.

> **Tip:** Use this for annual insurance, software subscriptions, or rent paid in advance.

### 12.3 Multi-Currency

Enable: **Accounting → Settings → Currencies**.

1. Turn on **Multi-Currencies**.
2. Add currencies under **Accounting → Configuration → Currencies**.
3. Set up exchange rates (manual or via API from central bank).
4. Create a **Foreign Currency Journal** (e.g. Bank USD).
5. Foreign-currency invoices/bills:
   - Select the foreign currency on the invoice.
   - Odoo converts using the current rate.
   - **Exchange Gain/Loss** is auto-calculated at payment/reconciliation.

> **Tip:** Run **Reporting → Audit Reports → Exchange Rate Gains/Losses** at month-end.

### 12.4 E-Invoicing (EDI / Peppol)

**Odoo 18 Enterprise** supports:

- **Peppol** (European e-invoicing network)
- **UBL XML** format
- **EDI** integrations

**Setup:**

1. **Accounting → Settings → Electronic Invoicing**.
2. Select **Peppol** provider (Delesy or other).
3. Enter your Peppol ID / VAT.
4. On invoices, click **Send & Print** → **Send by E-invoicing**.
5. Odoo sends the UBL XML + PDF via the Peppol network.

> **Tip:** Peppol is mandatory for B2G (government) in many EU countries.

### 12.5 Cash Flow Forecast

**Accounting → Reporting → Cash Flow Forecast**.

Odoo predicts future cash based on:

- Open invoices (expected incoming)
- Open bills (expected outgoing)
- Bank account balances

The forecast is visualised on a timeline.

> **Tip:** Update **Expected Date** on invoices for accurate forecasting.

### 12.6 Budget Management

**Accounting → Budgets**.

1. Create a **Budgetary Position** (account + analytic account).
2. Set **Budget Lines** (monthly/quarterly/annual amounts).
3. Create a **Budget** linking positions to a fiscal year.
4. Odoo compares actuals vs budget during the year.

**Reports:**

- **Budget Analysis** — actual vs committed vs planned.
- **Budget vs Actuals** — variance report.

> **Tip:** Use analytic accounts to track budgets by department / project.

---

## 13. SA-Specific (South Africa)

### 13.1 SARS Compliance

Odoo 18's **South African accounting package** (Community/Enterprise) includes:

- Default Chart of Accounts with SARS codes
- SARS-compliant invoice layouts
- VAT201 report template
- Withholding Tax support

### 13.2 VAT Reports

**SARS VAT201** (monthly/bi-monthly):

1. Go to **Reporting → Audit Reports → Tax Report**.
2. Select the **VAT** tax group.
3. Set the period (e.g. Jan 2026).
4. Click **Print** → select **VAT201** layout (Enterprise) or export to XLSX.

The report shows:

- Output VAT (Box 1 / 2)
- Input VAT (Box 14 / 15)
- Net VAT Payable / Refundable

> **Tip:** Verify against Trial Balance before filing. Reconcile the VAT Control Account each period.

### 13.3 EMP201 / EMP501 (Payroll Integration)

If you use Odoo Payroll (or a 3rd-party integration):

| Report | Frequency | Purpose |
|---|---|---|
| **EMP201** | Monthly | PAYE, SDL, UIF declaration & payment |
| **EMP501** | Bi-annual (Feb & Aug) | Year-to-date reconciliation |

**EMP201 workflow:**

1. Payroll runs → generates Payslips.
2. Approve Payslips → Odoo creates PAYE liability journal entries.
3. **Accounting → Payroll Reports → EMP201**.
4. Select period → **Generate** → print PDF or export.

**EMP501 workflow:**

1. After the bi-annual reconciliation period.
2. Generate EMP501 report.
3. Verify against IRP5/IT3(a) certificates.
4. Submit via SARS eFiling.

> **Tip:** Set up PAYE, SDL, and UIF as **Purchase Taxes** with SARS codes in the tax configuration.

### 13.4 Withholding Tax

For payments to vendors where WHT applies:

1. Set up WHT tax rates (e.g. 7.5% on interest, 15% on dividends).
2. On the vendor bill, apply the WHT tax line.
3. When registering the payment, Odoo nets the WHT amount.
4. A WHT liability account is credited until remitted.

### 13.5 Invoice Layouts

Odoo 18 SA includes **SARS-compliant invoice templates**:

- Tax invoices must show: VAT number, tax amounts per rate, total including VAT.
- Credit notes must show: reference to original invoice, reason for credit.

> **Tip:** Check **Accounting → Settings → Documents → Invoice Layout** for "South Africa" template.

---

## 14. Common Workflows

### 14.1 Daily: Record Customer Payment

1. **Accounting → Customers → Invoices**.
2. Find the paid invoice (use filter: **Unpaid**).
3. Open invoice → **Register Payment**.
4. Enter amount, date, bank journal.
5. Click **Register Payment**.
6. *(Optional)* Send receipt: **Send & Print → Receipt**.

### 14.2 Daily: Pay Vendor Bills

1. **Accounting → Vendors → Bills**.
2. Select bills to pay (checklist).
3. Click **Action → Register Payment**.
4. Choose payment method, bank journal, payment date.
5. **Create Payment**.

OR use **Batch Payment** for many bills.

### 14.3 Weekly: Reconcile Bank Account

1. **Accounting → Overview** → click the bank journal card.
2. Click **New** to enter a manual statement, or **Import Statement**.
3. For each line:
   - Accept suggested match or
   - Create a write-off for small differences.
4. Click **Validate**.
5. Check the **Reconciled** balance matches your real bank balance.

### 14.4 Weekly: Send Overdue Reminders

1. **Accounting → Customers → Follow-up**.
2. Select overdue invoices.
3. Click **Send by Email** or **Send by Snail-Mail**.
4. Odoo uses predefined **Follow-up Levels** (1st reminder, 2nd reminder, final demand).

> **Tip:** Configure follow-up levels at **Accounting → Configuration → Follow-up Levels**.

### 14.5 Month-End: Run VAT Report

1. **Reporting → Audit Reports → Tax Report**.
2. Select your VAT tax group.
3. Set date range (e.g. 1–31 July 2026).
4. Click **Print** → PDF or export.
5. Verify totals match Trial Balance VAT accounts.
6. File with SARS.

### 14.6 Month-End: Close the Period

1. Ensure all bank accounts are reconciled.
2. Run Trial Balance — fix any odd balances.
3. Post any accruals / deferrals.
4. Generate management reports (P&L, Balance Sheet).
5. Set lock dates:
   - **Invoicing Lock Date** = last day of the month.
   - **Accounting Lock Date** = last day of the month.
6. Archive the period.

### 14.7 Year-End: Fiscal Year Close

1. Run full P&L and Balance Sheet.
2. Post retained earnings closing entry:
   ```
   Debit: Net Income (temporary account)
   Credit: Retained Earnings
   ```
3. Close the fiscal year in **Configuration → Fiscal Years**.
4. Verify opening balances in the new year.

### 14.8 Setting Up a New Company

1. **Settings → General Settings → Company** → fill in details.
2. **Accounting → Settings** → enable chart of accounts.
3. Odoo installs the **SA Chart of Accounts** (or your localisation).
4. Add bank accounts as **Bank Journals**.
5. Set opening balances:
   - **Accounting → Accounting → Journal Entries** → **New**.
   - Post the opening balance entry with opening date.
6. Reconcile opening where applicable.

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` | Confirm / Post |
| `Alt + E` | Edit mode |
| `Alt + D` | Delete |
| `Ctrl + P` | Print |
| `Ctrl + S` | Save & stay |
| `Alt + F9` | Open full debug menu |

---

## Appendix B: Common Error Messages

| Error | Likely Cause | Fix |
|---|---|---|
| "Account not set" | Missing account on product or journal | Set default accounts in settings or product form |
| "Tax not configured" | Tax missing distribution lines | Edit tax → fill distribution for invoices/credit notes |
| "Lock date prevents posting" | Date is before lock date | Change the lock date or use a later date |
| "Cannot reconcile different partners" | Payment from Customer A matched to invoice of Customer B | Unmatch and match the correct partner |
| "Exchange rate not found" | No rate for currency on that date | Add daily rate in Currencies |

---

*End of document.*
