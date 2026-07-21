# Banking & Payments User Guide
## Payment Modes, Orders and SEPA in Odoo 18 (OCA Bank-Payment Collection)

---

**Document Version:** 1.0  
**Module:** OCA bank-payment (account_banking_payment)  
**Applies to:** Odoo 18 Enterprise & Community  

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites & Configuration](#prerequisites--configuration)
3. [Payment Modes and Methods](#payment-modes-and-methods)
4. [Banking Mandates](#banking-mandates)
5. [Payment Orders](#payment-orders)
6. [SEPA Credit Transfers](#sepa-credit-transfers)
7. [SEPA Direct Debits](#sepa-direct-debits)
8. [Payment Returns](#payment-returns)
9. [Partner Aging Reports](#partner-aging-reports)
10. [Check Printing](#check-printing)
11. [Appendix: Troubleshooting](#appendix-troubleshooting)

---

## Overview

The **OCA Bank-Payment Collection** suite provides a comprehensive payment processing framework for Odoo. It enables:

- Centralised payment order management (suppliers and customers)
- SEPA Credit Transfer (SCT) and SEPA Direct Debit (SDD) processing
- Banking mandate lifecycle management
- Payment return handling and reconciliation
- Check layout customisation and printing
- Multi-bank, multi-currency payment processing

### Key Concepts

| Term | Definition |
|------|------------|
| **Payment Mode** | High-level configuration linking payment method, journal, and mandate rules |
| **Payment Method** | The technical payment mean (SEPA CT, SEPA DD, Check, Wire Transfer) |
| **Payment Order** | A batch of payments grouped for processing together |
| **Mandate** | A signed authorisation from a debtor allowing direct debits |
| **Payment Return** | A rejected or returned payment received from the bank |

---

## Prerequisites & Configuration

### Required Modules

| Module | Technical Name | Purpose |
|--------|---------------|---------|
| Account Banking Payment | account_banking_payment | Core payment order engine |
| Account Banking Mandate | account_banking_mandate | SEPA mandate management |
| Account Banking SEPA Credit Transfer | account_banking_sepa_credit_transfer | SEPA CT generation |
| Account Banking SEPA Direct Debit | account_banking_sepa_direct_debit | SDD file generation |
| Account Banking Check Printing | account_banking_check_printing | Check layouts |

### Initial Setup Steps

1. **Install the modules**
   - Navigate to **Apps** → search for the module name
   - Install each desired module

2. **Configure bank journals**
   - Go to **Invoicing** → **Configuration** → **Journals**
   - For each bank account, edit the journal and ensure:
     - **Type** is set to `Bank`
     - **Bank Account** is correctly linked
     - **Currency** is set appropriately
     - **Payment Methods** tab lists all applicable methods

3. **Configure company bank accounts**
   - Go to **Invoicing** → **Configuration** → **Bank Accounts**
   - Enter your IBAN, BIC, and bank details
   - For SEPA: ensure IBAN and BIC are correct

> **Tip:** Use a **Test Bank Journal** with a separate bank account for sandbox testing before going live.

---

## Payment Modes and Methods

### Payment Methods

Defined at **Invoicing** → **Configuration** → **Payment Methods**.

| Method | Technical Code | Use Case |
|--------|---------------|----------|
| **Manual** | manual | Free-text payment entry |
| **Wire Transfer** | wire_transfer | Standard bank transfer (manual) |
| **SEPA Credit Transfer** | sepa_credit_transfer | Batch supplier payments |
| **SEPA Direct Debit** | sepa_direct_debit | Batch customer collections |
| **Check** | check_printing | Physical cheque printing |
| **Payment order** | payment_order | Generic batch processing |

#### Creating a Payment Method

1. Go to **Invoicing** → **Configuration** → **Payment Methods**
2. Click **Create**
3. Set the following:

   | Field | Description |
   |-------|-------------|
   | **Name** | Display name (e.g., "SEPA B2B Direct Debit") |
   | **Code** | Technical identifier |
   | **Payment Type** | `Inbound` (receive) or `Outbound` (send) |
   | **SEPA Scheme** | For SEPA methods: `CORE`, `B2B`, etc. |

4. Save

### Payment Modes

Defined at **Invoicing** → **Configuration** → **Payment Modes**.

A payment mode bundles:
- A **Payment Method**
- A **Bank Journal**
- A **Payment Order Sequence**
- Optional **mandate** requirements

#### Creating a Payment Mode

1. Go to **Invoicing** → **Configuration** → **Payment Modes**
2. Click **Create**
3. Configure:

   | Field | Description |
   |-------|-------------|
   | **Name** | e.g., "Supplier SEPA CT - ING Bank" |
   | **Payment Method** | Select a configured payment method |
   | **Bank Journal** | The bank journal to use |
   | **Payment Order Sequence** | Auto-numbering for payment orders |
   | **Company** | Leave blank for all companies |

4. For **inbound** modes (customer → you):
   - Check **Mandate Required** if direct debits need mandates
5. Save

### Assigning Payment Modes to Partners

1. Open a **Contact** form (Customers or Vendors)
2. Go to the **Accounting** tab
3. Under **Payment Mode**:
   - **Customer Payment Mode**: Used when collecting from this customer
   - **Supplier Payment Mode**: Used when paying this vendor

> **Tip:** Set up a default payment mode per partner so it auto-populates on invoices and payment orders.

---

## Banking Mandates

Mandates are legal authorisations that allow you to collect payments via direct debit (SEPA SDD).

### Mandate Lifecycle

```
Draft → Valid → Signed → Active → Expired / Cancelled
```

### Creating a Mandate

1. Go to **Invoicing** → **Banking** → **Mandates**
2. Click **Create**
3. Fill in:

   | Field | Description |
   |-------|-------------|
   | **Partner** | The debtor |
   | **Mandate Type** | `recurring`, `one_off`, or `B2B` |
   | **Scheme** | `CORE` (consumer) or `B2B` (business) |
   | **Unique Mandate Reference** | Auto-generated (edit if needed) |
   | **Signature Date** | Date the mandate was physically signed |
   | **Start Date** | When it becomes active |
   | **End Date** | Expiry (leave empty for indefinite) |
   | **Debtor IBAN** | The debtor's bank account |
   | **Debtor BIC** | The debtor's bank BIC |

4. Click **Validate**
5. The mandate moves to **Active** status

### Managing Mandate Statuses

| Status | Meaning | Next Action |
|--------|---------|-------------|
| **Draft** | Being created | Complete fields → Validate |
| **Valid** | Awaiting signature | Obtain signed copy → Mark Signed |
| **Signed** | Signed but not yet active | Arrive at Start Date → auto-activates |
| **Active** | Ready for collections | Can be used in SDD payment orders |
| **Expired** | Past End Date | Create new mandate or renew |
| **Cancelled** | Revoked by partner | Use a new mandate for future collections |

### Amending a Mandate

1. Open the mandate
2. Click **Amend**
3. Update the relevant fields (e.g., new IBAN)
4. The original mandate is closed; a new version is created with a new UMR

### Mandate Reporting

- **Mandate Analysis Report**: View all mandates by status, partner, scheme
- Access at **Invoicing** → **Reporting** → **Mandate Analysis**

> **Tip:** Configure **Mandate Expiry Alerts** in *Settings → Technical → Scheduled Actions → Mandate Expiry Alert* to notify you 30 days before mandates expire.

---

## Payment Orders

A **Payment Order** groups multiple payments into a single batch for processing.

### Creating a Payment Order

1. Go to **Invoicing** → **Banking** → **Payment Orders**
2. Click **Create**
3. Configure the header:

   | Field | Description |
   |-------|-------------|
   | **Payment Mode** | Select the payment mode |
   | **Payment Type** | `Inbound` (collect) or `Outbound` (pay) |
   | **Date** | Execution date |
   | **Date Execution** | Date to be executed by the bank |
   | **Journal** | Bank journal (auto-filled from mode) |
   | **Company** | Your company entity |

4. Click **Save**

### Adding Payments to an Order

**Method 1 — From the Payment Order:**
1. In the **Payment Lines** tab, click **Add a line**
2. Select a **Partner**
3. Choose the **Invoice** to pay/collect
4. The **Amount**, **Communication**, and **Partner Bank** auto-fill
5. Verify and click **Save**

**Method 2 — From Invoices (Recommended):**
1. Open an invoice that is in **Open** or **Posted** status
2. Click **Action** → **Register Payment**
3. Select the **Payment Method** (linked to a payment order mode)
4. The payment is automatically added to the next draft payment order for that mode

**Method 3 — Batch from Invoices (Most Efficient):**
1. Go to **Invoicing** → **Customers** → **Invoices**
2. Use filters to select multiple invoices (e.g., all "Due Today")
3. Click **Action** → **Create Payment Order**
4. System groups them into a payment order

### Payment Order States

| State | Meaning |
|-------|---------|
| **Draft** | Editable; payments can be added/removed |
| **Open** | Locked; being reviewed; no further modifications |
| **Generated** | Payment file created (e.g., SEPA XML) |
| **Uploaded** | File sent to bank |
| **Done** | All payments reconciled |
| **Cancelled** | Order voided |

### Processing a Payment Order

1. In **Draft**: Review all payment lines for accuracy
2. Click **Confirm** → status changes to **Open**
3. Click **Generate** → creates the bank file (e.g., `.xml` for SEPA)
4. Click **Download File** → save to your computer
5. **Upload** the file to your online banking portal
6. After bank confirmation, click **Uploaded** to mark
7. Click **Create Payment** → Odoo creates account moves
8. Click **Done** to complete

> **Tip:** Create a **Payment Order Template** with pre-filled payment mode and journal for recurring batches (e.g., monthly supplier runs).

---

## SEPA Credit Transfers

SEPA Credit Transfers (SCT) are used for outbound payments (paying suppliers).

### Generating an SCT File

1. Create a **Payment Order** with:
   - **Payment Mode**: Set to SEPA Credit Transfer
   - **Payment Type**: Outbound
2. Add payment lines (supplier invoices due)
3. **Confirm** the order
4. Click **Generate** → Odoo creates a SEPA XML file (ISO 20022)
5. **Download** the XML file

### SEPA XML File Content

The generated file includes for each payment:
- **Debtor** (your company): Name, IBAN, BIC
- **Creditor** (supplier): Name, IBAN, BIC
- **Amount**: In EUR (SEPA only supports EUR)
- **Remittance Information**: Invoice reference(s)
- **Execution Date**: Requested execution date

### Uploading to the Bank

1. Log in to your corporate banking portal
2. Navigate to **SEPA Credit Transfer Upload**
3. Upload the `.xml` file
4. Review the parsed payments
5. Authorise with electronic signatures
6. Download the bank's confirmation report

### Handling the Bank Confirmation

1. In Odoo, go back to the **Payment Order**
2. Click **Create Payment** to generate accounting entries
3. Verify: open each invoice → status should change to **Paid**
4. Click **Done** to finalise

### Multi-Currency Considerations

- SEPA **only** supports EUR
- For non-EUR payments, use **Wire Transfer** instead
- Configure a separate Payment Mode for non-SEPA payments

> **Tip:** Always set the **Execution Date** at least 1 banking day before the due date to allow for processing time.

---

## SEPA Direct Debits

SEPA Direct Debits (SDD) are used for inbound collections (collecting from customers).

### SDD Schemes

| Scheme | Description | Notice Period |
|--------|-------------|---------------|
| **CORE** | Consumer customers | 14 days (first), 5 days (recurring) |
| **B2B** | Business customers | 1 day (no refund right) |

### Prerequisites for SDD

Before you can generate an SDD payment order:

1. **Mandates** must be signed and **Active** for each debtor
2. **Partner bank accounts** must have IBAN and BIC filled
3. **Payment Mode** must be configured with SDD method

### Generating an SDD File

1. Go to **Invoicing** → **Customers** → **Invoices**
2. Use filters: **Due Today** + **Open**
3. Select relevant invoices
4. Click **Action** → **Create Payment Order**
5. The system creates a new **Payment Order** in Draft with:
   - **Payment Mode**: Auto-selected from customer's payment mode
   - **Payment Type**: Inbound
   - **Payment Lines**: One per invoice with mandate reference attached
6. **Confirm** the order
7. Click **Generate** → the SDD XML file is created (ISO 20022 `pain.008.001.02`)

### Pre-Notification (Prenotification)

For CORE SDD, you must send a **prenotification** at least 14 days before the first collection and 5 days before recurring collections.

1. From the Payment Order, click **Send Prenotification**
2. The system generates a PDF for each debtor showing:
   - Creditor name and identifier
   - Amount to be collected
   - Due date
   - Mandate reference
3. Email the prenotification to each debtor

### SDD Flow Summary

```
Create Payment Order → Confirm → Send Prenotification (wait notice period)
→ Generate SDD XML → Upload to Bank → Bank processes (due date)
→ Receive bank statement → Reconcile → Click Done
```

### Failed Direct Debits (R-Transactions)

If a direct debit fails (e.g., insufficient funds):
1. The bank sends an **R-Transaction** (return)
2. Record this as a **Payment Return** (see section below)
3. The customer's invoice is automatically set back to **Open** (unpaid)
4. Decide to retry or contact the customer

> **Tip:** For B2B SDD, ensure you have a signed mandate on file — the 14-month refund right does not apply, but the mandate must be B2B scheme.

---

## Payment Returns

A **Payment Return** is a transaction returned by the bank. This can apply to both inbound (failed direct debit) and outbound (rejected transfer) payments.

### Creating a Payment Return

**Automatic Method (from bank statement):**
1. When importing a bank statement, Odoo detects return transactions
2. A **Payment Return** is auto-created
3. Link it to the original payment order

**Manual Method:**
1. Go to **Invoicing** → **Banking** → **Payment Returns**
2. Click **Create**
3. Fill in:

   | Field | Description |
   |-------|-------------|
   | **Payment Order** | The original order containing the returned payment |
   | **Payment Line** | The specific payment that was returned |
   | **Return Reason** | See table below |
   | **Return Amount** | Amount returned (currency) |
   | **Return Date** | Date the bank processed the return |
   | **Journal** | Bank journal |

4. Click **Confirm**

### Standard Return Reason Codes (SEPA)

| Code | Meaning |
|------|---------|
| AC01 | Incorrect IBAN |
| AC04 | Closed account |
| AC06 | Blocked account |
| AG01 | Account blocked for DDs |
| AM04 | Insufficient funds |
| AM05 | Duplicate payment |
| BE01 | Incorrect creditor identifier |
| MD01 | Mandate cancelled |
| MD06 | Mandate expired |
| RR01 | Insufficient mandate information |

### Reconciling a Return

When a payment return is confirmed:
- **Inbound (DD)**: The customer invoice is set back to **Open** (unpaid)
- **Outbound (CT)**: The supplier invoice is set back to **Open** (unpaid)
- The return generates a **reconciliation move** in the bank journal

### Retrying a Failed Payment

1. After the return is processed, go to the original **Invoice**
2. Verify the partner's bank details are correct
3. If necessary, update the **Mandate** or bank account
4. Re-add the invoice to a new **Payment Order**

> **Tip:** Use the **Payment Return Analysis** report (*Invoicing → Reporting → Payment Return Analysis*) to track return rates and identify problematic partners.

---

## Partner Aging Reports

Aging reports show outstanding receivables and payables grouped by time buckets.

### Opening the Aging Report

1. Go to **Invoicing** → **Reporting** → **Aged Receivable**
   - Or **Aged Payable** for supplier balances
2. As of date: defaults to today
3. Data is displayed in a pivot table

### Understanding the Columns

| Column | Period | Interpretation |
|--------|--------|----------------|
| **Not Due** | Future / Current | Invoices not yet due |
| **1-30 Days** | 1–30 days overdue | Early warning |
| **31-60 Days** | 31–60 days overdue | Need follow-up |
| **61-90 Days** | 61–90 days overdue | Escalate |
| **91+ Days** | > 90 days overdue | High risk; consider provisions |
| **Total** | All periods | Total outstanding balance |

### Filtering and Grouping

Use the **Filters** and **Group By** options:

| Filter | Example Use Case |
|--------|------------------|
| **Partner** | Check a specific customer's aging |
| **Company** | Multi-company filtering |
| **Currency** | View aging per currency |

| Group By | Example Use Case |
|----------|------------------|
| **Partner** | List all customers with balances |
| **Salesperson** | Review by account manager territory |
| **Payment Term** | Analyse impact of payment terms |

### Exporting the Aging Report

1. Click the **gear icon** ⚙ → **Export All**
2. Select **XLSX** format for Excel
3. Choose fields: Partner, Total Due, 1-30, 31-60, 61-90, 91+
4. Click **Export**
5. Use for weekly credit control meetings

### Using Aging for Dunning

The aging report feeds into Odoo's **Dunning** process:

1. Go to **Invoicing** → **Customers** → **Dunning**
2. Click **Create Dunning** from the aging view
3. The system groups overdue invoices by partner
4. Send automated dunning letters based on aging bucket

> **Tip:** Schedule the **Aged Receivable** report to be emailed weekly to the credit control team via *Action → Send by Email → Set Scheduled Report*.

---

## Check Printing

The **Account Banking Check Printing** module supports custom check layouts and batch printing.

### Configuration

1. Install `account_banking_check_printing`
2. Go to **Invoicing** → **Configuration** → **Check Layouts**
3. Click **Create** to define a new check layout

### Check Layout Configuration

| Field | Description |
|-------|-------------|
| **Name** | Layout name (e.g., "Standard US Check") |
| **Check Size** | Standard or custom dimensions |
| **Left Margin** | Left offset (mm) |
| **Top Margin** | Top offset (mm) |
| **Date Format** | `DD/MM/YYYY` or `MM/DD/YYYY` |
| **Amount in Words** | Language for textual amount |
| **Number of Stubs** | 0, 1, or 2 stubs per check |
| **Bank Account** | Which bank account the check draws from |

### Custom Fields on Checks

You can place the following fields anywhere on the check layout:
- Payee name and address
- Amount (numeric and in words)
- Date
- Check number
- Company name and address
- Bank name, IBAN, BIC
- MICR line (magnetic ink character recognition)
- Stub details (invoice references)

### Printing Checks

1. Go to **Invoicing** → **Banking** → **Payment Orders**
2. Create a new **Payment Order** with:
   - **Payment Mode**: Check printing mode
   - **Payment Type**: Outbound
3. Add payment lines for suppliers to pay
4. **Confirm** the order
5. Click **Print Checks**
6. Select the **Check Layout**
7. Choose the **Starting Check Number**
8. Click **Print**
9. The system generates a PDF with all checks ready to print on pre-printed check paper

### Check Templates

Odoo supports multiple check paper formats:

| Format | Paper Type |
|--------|------------|
| **Pre-printed** | Bank-provided check stock with MICR |
| **Blank** | Plain paper; prints all fields including bank details |
| **Wallet Check** | Smaller check size for personal use |

### Manual Checks

For hand-written checks issued outside Odoo:

1. Go to an open supplier invoice
2. Click **Action** → **Register Payment**
3. Select **Check** as the payment method
4. Enter the **Check Number** and **Issue Date**
5. Validate → the invoice is marked Paid

### Check Cancellation

1. Go to **Invoicing** → **Banking** → **Checks**
2. Find the issued check
3. Click **Cancel Check**
4. The payment is reversed; the invoice is set back to **Open**

> **Tip:** Use **pre-numbered check stock** and enter the starting number in the payment order. Odoo will validate that the numbers are sequential and flag any gaps.

---

## Appendix: Troubleshooting

### Common Issues

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| **SEPA XML not generating** | Missing IBAN/BIC on partner or company | Verify bank details on partner form and company configuration |
| **Payment order stuck in Draft** | No payment lines added | Add invoices or create manual payment lines |
| **Mandate not appearing in SDD order** | Mandate is not in Active state | Check mandate status; verify start/end dates |
| **Check print fails** | Incorrect layout margins | Adjust Left/Top margin values by 2mm increments |
| **Aging report shows wrong amounts** | Reconciliation issues | Run *Invoicing → Actions → Reconcile* for the partner |

### Validation Checklist (Before Going Live)

- [ ] Bank journals configured with correct accounts
- [ ] Payment methods created (SEPA CT, SDD, Check)
- [ ] Payment modes created and linked to journals
- [ ] Partner bank accounts have IBAN/BIC
- [ ] Mandates collected and activated for SDD customers
- [ ] Check layouts tested with sample paper
- [ ] SEPA XML files tested in sandbox
- [ ] Payment return handling tested

---

## Appendix: Key Navigation Shortcuts

| Action | Navigation Path |
|--------|----------------|
| Payment Modes | Invoicing → Configuration → Payment Modes |
| Payment Methods | Invoicing → Configuration → Payment Methods |
| Mandates | Invoicing → Banking → Mandates |
| Payment Orders | Invoicing → Banking → Payment Orders |
| Payment Returns | Invoicing → Banking → Payment Returns |
| Check Layouts | Invoicing → Configuration → Check Layouts |
| Aged Receivable | Invoicing → Reporting → Aged Receivable |
| Aged Payable | Invoicing → Reporting → Aged Payable |

---

*End of Document*
