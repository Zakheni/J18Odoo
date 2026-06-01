# Zakheni Odoo 18 — User Manual

## Zakheni ICT (Pty) Ltd

---

## 1. Getting Started

### 1.1 Logging In

1. Open your browser and navigate to `http://<server-ip>:8069`
2. Enter your **Username** and **Password**
3. Click **Log In**

> **Default admin credentials**: `admin` / `admin` (change on first login)

### 1.2 Navigation Overview

The main menu bar at the top contains all apps you have access to:

| App | Description |
|-----|-------------|
| **Invoicing** | Accounting, invoices, payments, bank reconciliation |
| **Helpdesk** | Customer support tickets |
| **Sales** | Orders, quotations, CRM |
| **Contacts** | Customers, vendors, partners |
| **Employees** | HR, contracts, leaves |
| **Settings** | System configuration |

Under **Invoicing**, you will find the **Enterprise Accounting** submenu with our custom features:

```
Invoicing
├── Dashboard
├── Customers
├── Vendors
├── Accounting
├── Reporting
├── Configuration
└── Enterprise Accounting     ← Custom features
    ├── Dashboard
    ├── Cash Flow Forecast
    ├── Follow-up Plans
    └── Consolidations
```

---

## 2. Helpdesk Module

### 2.1 Overview

The helpdesk module routes customer support tickets to the correct team automatically. Each customer is assigned to a specific helpdesk team. When that customer creates a ticket, it is automatically assigned to their team.

### 2.2 Assigning a Customer to a Team

1. Go to **Contacts**
2. Open the customer's contact record
3. Go to the **Helpdesk** tab
4. Set the **Helpdesk Team** field to the appropriate team
5. Save

![Contact Helpdesk Team](https://via.placeholder.com/600x200?text=Helpdesk+Team+field+on+Contact)

### 2.3 Creating a Helpdesk Team

1. Go to **Helpdesk → Configuration → Teams**
2. Click **Create**
3. Enter:
   - **Team Name** (e.g., "Level 1 Support")
   - **Assigned Members** — team members
   - **Team Leaders**
4. Save

### 2.4 Creating a Ticket

1. Go to **Helpdesk → Tickets**
2. Click **Create**
3. Enter:
   - **Subject** — brief description
   - **Customer** — the customer reporting the issue
     - The **Team** field auto-fills based on the customer's assigned team
   - **Priority** — Low / Normal / High / Urgent
   - **Description** — detailed explanation
4. Click **Save**

The ticket is now assigned to the correct team automatically.

### 2.5 Working on a Ticket

1. Open a ticket from the list
2. The **Assigned To** field shows which team member is responsible
3. Update the **Stage** as work progresses:
   - **New** → **In Progress** → **Waiting on Customer** → **Resolved** → **Closed**
4. Use the ** chatter** (message log at the bottom) to communicate with the customer
5. Log **Timesheets** if tracking time

### 2.6 Ticket SLA Tracking

If SLA (Service Level Agreement) is enabled:
- SLA deadlines are shown on the ticket
- Turn green/yellow/red based on urgency and elapsed time
- Breaches are logged automatically

---

## 3. Enterprise Accounting

### 3.1 Dashboard

The Accounting Dashboard provides a bird's-eye view of your financial health.

Navigate to: **Invoicing → Enterprise Accounting → Dashboard**

**KPIs displayed:**
- **Bank Accounts** — count, total balance, pending statements
- **Invoices** — draft invoice count, overdue count, overdue total amount
- **Receivables** — total amount customers owe you
- **Payables** — total amount you owe vendors
- **Cash Flow Forecast** — projected cash position

**Quick Actions:**
- **Bank Statements** — view and reconcile bank transactions
- **Journal Items** — view all accounting entries
- **Customer Invoices** — create and manage sales invoices
- **Vendor Bills** — create and manage purchase bills

### 3.2 Cash Flow Forecast

Navigate to: **Invoicing → Enterprise Accounting → Cash Flow Forecast**

This shows your projected cash position over time.

**How it works:**
- **Inflow**: Open customer invoices (not yet paid) are included as expected inflows on their due date
- **Outflow**: Open vendor bills are included as expected outflows on their due date
- **Starting Balance**: Current bank account balance
- **Projected Balance**: Starting balance + inflows - outflows

**To regenerate the forecast:**
The forecast updates automatically via a scheduled cron job. You can also manually trigger it from the Dashboard.

### 3.3 Follow-up Plans (Dunning)

Navigate to: **Invoicing → Enterprise Accounting → Follow-up Plans**

#### Creating a Follow-up Plan

1. Click **Create**
2. Enter a **Name** (e.g., "Standard 30-day Dunning")
3. Add **Follow-up Levels** (the escalation steps):

| Level | Days After Due | Action | Email Template |
|-------|---------------|--------|----------------|
| 1 | 7 days | Send reminder email | First Reminder |
| 2 | 14 days | Send warning email | Second Notice |
| 3 | 21 days | Send final notice + fee | Final Demand |
| 4 | 30 days | Send to collections | Handover Notice |

4. Click **Save**

#### Assigning a Plan to a Customer

1. Go to **Contacts → [Customer]**
2. Open the **Accounting** tab
3. Set **Follow-up Plan** to the desired plan
4. Set **Follow-up Responsible** to the person handling collections
5. Save

#### Automated Dunning

The system runs a scheduled cron job daily that:
1. Checks all overdue invoices
2. Sends the appropriate dunning letter based on the customer's follow-up plan
3. Logs the follow-up date on the customer record

### 3.4 Credit Limits

Each customer can have a credit limit set on their contact record.

Navigate to: **Contacts → [Customer] → Accounting tab**

Fields:
- **Credit Limit** — maximum credit allowed (e.g., R50,000)
- **Credit Used** — current outstanding balance (auto-calculated)
- **Credit Available** — credit limit minus credit used
- **Credit Exceeded** — checkbox indicating limit is exceeded

When an invoice exceeds a customer's credit limit, the system will warn you during validation.

### 3.5 Consolidations

Navigate to: **Invoicing → Enterprise Accounting → Consolidations**

This allows you to consolidate financial data from multiple companies into a single view.

#### Creating a Consolidation

1. Click **Create**
2. Enter:
   - **Name** — e.g., "Q1 2026 Group Consolidation"
   - **Date** — period end date
   - **Target Company** — the consolidated entity
   - **Companies** — select which subsidiary companies to include
3. Click **Save**
4. Click **Compute Consolidation** — the system aggregates all account balances
5. Review the **Consolidation Lines** showing source company → target account mapping

> **Note**: Consolidation requires accounts to be mapped between companies. This is typically configured once during setup.

---

## 4. Partner Enrichment

### 4.1 Overview

The Partner Enrichment module automatically fills in missing company information using Google Custom Search. When you add a new customer or vendor, you can enrich their record with data found on the web.

### 4.2 Configuration (Admin Only)

Go to **Settings → General Settings → Partner Enrich** and enter:
- **Google API Key** — provided by Google Cloud Console
- **Google Search Engine ID (cx)** — from Programmable Search Engine

### 4.3 Enriching a Partner

1. Go to **Contacts** and open a partner record
2. Ensure the company **Name** is entered
3. Click the **Enrich from Web** button (visible for company-type contacts)
4. The system will:
   - Search Google for the company name
   - Visit the company's website
   - Extract: website URL, email addresses, phone numbers, address, description
5. Review the populated fields and save

> **Tip**: The enrichment works best with specific company names. Generic names may return incorrect results.

---

## 5. Document Management (DMS)

### 5.1 Overview

The Document Management System (DMS) stores and organizes files. It supports both local storage and SharePoint (Microsoft 365) as backends.

### 5.2 Uploading Documents

1. Go to **Documents**
2. Navigate to the desired directory/folder
3. Click **Upload** and select files, or drag-and-drop

### 5.3 SharePoint Integration

If configured with your Microsoft 365 account:

1. Go to **Settings → General Settings → SharePoint**
2. Authenticate with your Microsoft 365 account
3. Select the SharePoint site and document library
4. Documents will sync between Odoo and SharePoint

---

## 6. SARS Payroll

### 6.1 Overview

The payroll module is configured for South African compliance, including:
- PAYE (Pay-As-You-Earn) tax calculations
- UIF (Unemployment Insurance Fund)
- SDL (Skills Development Levy)
- Medical aid tax credits
- Pension fund contributions

### 6.2 Processing Payroll

1. Go to **Employees → Payroll**
2. Click **Create** to start a new payslip batch
3. Select the **Employees**, **Period**, and **Contract**
4. Click **Compute Sheet** — the system calculates all earnings and deductions
5. Review the payslip
6. Click **Confirm** and then **Post**

### 6.3 EMP201 / EMP501 Reports

1. Go to **Employees → Payroll → Reporting**
2. Select the required SARS report:
   - **EMP201** — Monthly PAYE declaration
   - **EMP501** — Bi-annual reconciliation
   - **IRP5** — Year-end employee tax certificate
3. Generate and export the file for SARS eFiling submission

### 6.4 SARS Numbers

Your company's SARS registration numbers are pre-configured:

| Number | Value |
|--------|-------|
| PAYE | 7205614930 |
| UIF | 7205614930 |
| SDL | S7205614930 |
| Registration | 7205614930 |

Update these in **Settings → General Settings** if your actual numbers differ.

---

## 7. Common Tasks

### 7.1 Creating a Customer Invoice

1. **Invoicing → Customers → Customer Invoices**
2. Click **Create**
3. Select **Customer**
4. Add **Invoice Lines** (products/services)
5. Set **Due Date** for payment terms
6. Click **Confirm**
7. Click **Post** to make it official
8. Click **Send & Print** to email the invoice to the customer

### 7.2 Recording a Payment

1. Open the invoice you want to pay
2. Click **Register Payment**
3. Select **Payment Method** (EFT, Credit Card, Cheque, etc.)
4. Enter the **Amount**
5. Select the **Bank Account**
6. Click **Validate**

### 7.3 Bank Reconciliation

1. **Invoicing → Accounting → Bank Statements**
2. Open a bank statement
3. Click **Reconcile** — the system suggests matching invoices/payments
4. Confirm the matches
5. Click **Validate**

### 7.4 Viewing Aged Receivables

1. **Invoicing → Reporting → Partner Reports → Aged Receivable**
2. The report shows amounts by aging period:
   - Current
   - 1–30 days overdue
   - 31–60 days overdue
   - 61–90 days overdue
   - 90+ days overdue

### 7.5 Creating a Journal Entry

1. **Invoicing → Accounting → Journal Entries**
2. Click **Create**
3. Select **Journal** (Miscellaneous Operations)
4. Add **Debit** and **Credit** lines
5. Click **Post**

---

## 8. Roles & Permissions

| Role | Access |
|------|--------|
| **Administrator** | Full access to all modules and settings |
| **Accountant** | Full accounting access, reporting |
| **Invoicing User** | Create/edit invoices, payments |
| **Helpdesk Agent** | Manage tickets assigned to their team |
| **Helpdesk Manager** | Manage all tickets, teams, SLAs |
| **Employee** | View own payslips, submit leave requests |

To assign roles: **Settings → Users & Companies → Users → [User] → Access Rights**

---

## 9. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Save current record |
| `Ctrl+S` | Quick save (if autosave is off) |
| `Alt+T` | Open search/filter |
| `Ctrl+Alt+K` | Toggle keyboard shortcuts help |
| `Escape` | Close popup / cancel |
| `Ctrl+Shift+F` | Full-screen mode |

---

## 10. Getting Help

If you encounter issues:

1. **Check the logs** — ask your system administrator for the Odoo log file
2. **Module documentation** — each module's settings are documented inline with help text
3. **Odoo Community** — https://www.odoo.com/forum/help-1
4. **Zakheni ICT Support** — contact your internal IT support team

---

## Appendix A: Module Dependencies

```
zakheni_config
  └── account (Invoicing)

zakheni_helpdesk
  ├── helpdesk_mgmt
  └── contacts

zakheni_partner_enrich
  ├── account
  └── contacts

zakheni_accounting
  ├── account
  ├── account_due_list
  ├── partner_aging
  ├── account_spread_cost_revenue
  ├── account_reconcile_oca
  └── account_fiscal_year
```

---

## Appendix B: Scheduled Actions (Cron Jobs)

| Name | Schedule | Purpose |
|------|----------|---------|
| Zakheni Accounting: Auto Follow-up | Daily 01:00 | Checks overdue invoices and sends dunning letters |
| Zakheni Accounting: Generate Cash Forecast | Daily 02:00 | Recalculates cash flow projections |
| Mail Digest | Weekly | Sends email summaries to users |

---

*Document version 1.0 — Zakheni ICT (Pty) Ltd*
