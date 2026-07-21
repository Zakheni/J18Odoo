# 01 — Sales-to-Cash Workflow (Order-to-Cash)
**Module**: CRM → Sales → Inventory → Accounting
**Version**: Odoo 18

---

## Overview

The Sales-to-Cash workflow spans five Odoo modules and represents the complete revenue cycle — from identifying a potential customer to receiving money in the bank.

```
CRM ──→ Sales ──→ Inventory ──→ Accounting ──→ Accounting
Lead      Quotation    Delivery       Invoice        Payment
 │            │            │              │             │
Opportunity  SO Confirm   Picking        Validate    Register
                 │            │
                 └──── MTO ───┘   (if Make-to-Order)
```

### Swimlane — Role Responsibility Matrix

| Step | Sales Rep | Sales Manager | Inventory User | Inventory Manager | Accountant |
|------|-----------|---------------|----------------|-------------------|------------|
| 1. Lead/Opportunity | Create & Qualify | — | — | — | — |
| 2. Quotation → SO | Confirm | Approval (if > threshold) | — | — | — |
| 3. Delivery Order | — | — | Pick & Validate | Validate Packed | — |
| 4. Customer Invoice | View | View | — | — | Create & Validate |
| 5. Payment | — | — | — | — | Register Payment |
| 6. Reconciliation | — | — | — | — | Reconcile |

---

## Step 1 — Lead / Opportunity in CRM → Convert to Quotation

### Who
**Sales Rep** creates and qualifies leads.

### Procedure

1. **Navigate**: CRM → Leads → Create
   - ![Screenshot Description: Leads list view with a "Create" button top-left. A lead form opens showing "New Lead" at the top.]
2. Fill mandatory fields:
   - **Customer**: Select existing or create a new contact
   - **Expected Revenue**: Estimated deal value
   - **Probability**: Manually set or auto-computed by stage
   - **Responsible**: Assigned Sales Rep (defaults to current user)
3. **Qualify the Lead**:
   - Click the "Qualify" smart-button at the top of the form
   - System converts the Lead into an **Opportunity** (same form, now with pipeline stage tracking)
   - ![Screenshot Description: Lead form after qualification — the top shows "Opportunity" label, a Kanban-stage selector, and additional smart-buttons for Quotation, Meeting, etc.]
4. **Convert to Quotation**:
   - On the Opportunity form, click **"New Quotation"** (top action bar)
   - A Sales Order draft is automatically pre-filled with:
     - Customer
     - Pricelist (from customer or default)
     - Payment Terms
   - Add products (Order Lines tab)
   - Set quantities, unit prices, taxes
   - ![Screenshot Description: Quotation form showing order lines with product, quantity, unit price, taxes, and subtotal columns.]
5. **Alternative — Direct from Pipeline Dashboard**:
   - CRM → Pipeline → drag Opportunity to "Quotation" stage
   - Click the money-icon action to auto-generate a quotation

### Approval Triggers
- None at this stage; the quotation is still a draft.

---

## Step 2 — Quotation → Sales Order

### Who
**Sales Rep** confirms; **Sales Manager** may need to approve if total exceeds the configured approval limit.

### Procedure

1. **Review Quotation**: Sales → Quotations → find the draft quotation
   - ![Screenshot Description: Quotation list filtered by "Quotations" with status "Draft". Each row shows Reference, Customer, Total, and Confirmation Date (empty).]
2. **Send Quotation to Customer** (optional):
   - Click **"Send by Email"** — Odoo generates a PDF quotation attached to a template email
   - Customer can accept via the customer portal (online acceptance)
      - If portal-accepted, status auto-advances
3. **Confirm Order**:
   - Click **"Confirm"** button (top of the form)
   - The quotation becomes a **Sales Order**:
     - Status changes from *Quotation* to *Sales Order*
     - A new entry in Sales → Orders → Sales Orders
     - Inventory moves / manufacturing orders are auto-created based on product type
     - ![Screenshot Description: Sales Order form after confirmation — smart-buttons now show "Delivery" (if stockable), "Invoice", "Picking". Status reads "Sales Order".]

### Approval Workflow (if enabled)
- If the sales total > **Sales Team → Configuration → Approval Limit**:
  - Quotation status is *Waiting Approval*
  - **Sales Manager** opens the quotation → **"Approve"** button appears
  - After approval, "Confirm" becomes available

### Cross-Module Impact
| Product Type | Effect on Confirm |
|--------------|------------------|
| **Stockable** | Draft Delivery Order created in Inventory → Pickings |
| **Service** | No inventory impact |
| **Consumable** | No inventory impact |

---

## Step 3 — Sales Order → Delivery Order (Inventory)

### Who
**Inventory User** processes the picking; **Inventory Manager** validates if double-validation is enabled.

### Procedure

1. **Navigate**: Inventory → Operations → Pickings
   - ![Screenshot Description: Picking list filtered by "Ready" state. Shows Reference, Scheduled Date, Partner, Source Location.]
2. **Check Availability**:
   - Open the delivery order (reference matches the SO)
   - Click **"Check Availability"** (or the button appears on the form)
   - Odoo checks on-hand stock at the source location
   - If sufficient: status becomes *Available* (ready to pick)
   - If insufficient: status remains *Waiting*, partial picking may be set up
3. **Process the Picking**:
   - Click **"Validate"** to open the detailed operations wizard
   - In the wizard:
     - Verify product, quantity, lot/serial numbers (if tracked)
     - ⚠️ **Scrap**: If a product is damaged during picking, click "Scrap" to move it to the scrap location
     - ![Screenshot Description: Validate wizard showing product lines with quantities, lot/serial fields, "Done" and "Scrap" buttons. A checkbox "Create Backorder" is visible for partial deliveries.]
   - Click **"Validate"** to confirm
   - If the delivery is partial: system prompts to create a **Backorder** (remaining qty = new delivery order)
4. **Result**:
   - Delivery status = *Done*
   - Stock valuation journal entry created
   - Smart-button on SO now shows **"Delivered"**
   - Invoice button becomes available

### Special Scenarios

| Scenario | Handling |
|----------|----------|
| Partial Delivery | System auto-creates a backorder for remaining qty |
| Over Delivery | Configurable tolerance in Product → Inventory → Reordering Rules |
| Return | Inventory → Reverse → Return; creates a Return picking |

---

## Step 4 — Delivery → Customer Invoice (Accounting)

### Who
**Accountant** or a user with *Invoicing* access performs this step. In some companies an **Inventory User** can trigger via the "Create Invoice" button on the SO.

### Procedure

1. **Navigate**: Sales → Orders → Sales Orders → select the delivered SO
2. Click **"Create Invoice"** button (appears only after delivery is validated)
   - ![Screenshot Description: Invoice creation wizard with options: "Regular invoice" (percentage delivered), "Down payment", or "Final invoice". A checkbox "Group invoice" if multiple SOs need consolidation.]
3. Choose invoicing method:
   | Option | When Used |
   |--------|-----------|
   | Regular Invoice (based on delivered qty) | Standard — invoices only what was delivered |
   | Down Payment | Advance payment before delivery |
   | Final Invoice | Remaining balance after down payments |
4. Odoo creates a **Draft Invoice** in Accounting → Customer Invoices
   - ![Screenshot Description: Draft invoice form — Vendor Bill counterpart. Shows Invoice Date, Due Date, Journal, Invoice Lines (auto-populated from SO lines delivered), Taxes section, and Total.]
5. **Validate the Invoice**:
   - Click **"Validate"** (top button)
   - Status changes:
     - *Draft* → *Posted* (or *Open* in non-ANG)
     - Journal Entry created in account move
     - Accounting → Customers → Aged Receivable updated
6. **Send to Customer** (optional):
   - **"Send & Print"** button → email PDF to customer

### Accounting Impact

| Account | Debit | Credit |
|---------|-------|--------|
| Receivable (customer account) | Invoice Total | — |
| Revenue (product income account) | — | Subtotal |
| Tax (tax account) | — | Tax Amount |

---

## Step 5 — Invoice → Payment Registration

### Who
**Accountant** receives and registers the payment.

### Procedure

1. Navigate to the posted invoice: Accounting → Customers → Invoices → select the invoice
2. Click **"Register Payment"** button
   - ![Screenshot Description: Payment registration dialog. Fields: Amount (defaults to open balance), Payment Date, Payment Method (Manual, Check, Bank), Journal (Bank or Cash Journal), Partner Bank Account, and a checkbox "Send Payment Receipt to Customer".]
3. Fill the payment dialog:
   - **Amount**: defaults to *Residual* (unpaid balance); can be changed for partial payments
   - **Payment Date**: actual date money was received
   - **Payment Method**: Manual / Check / Electronic
   - **Journal**: select the Bank Journal or Cash Journal
   - **Partner Bank Account**: auto-filled if on file
   - **Memo**: optional reference
4. Click **"Create Payment"**
5. Result:
   - Payment record created in Accounting → Customers → Payments
   - Invoice status changes:
     - *Open* → *Paid* (if fully paid)
     - *Open* → *Partial* (if underpaid)
   - Payment Method journal entry created:
     - Debit: Bank Account
     - Credit: Receivable (clears the invoice receivable line)

### Partial / Multi-Payment

| Situation | How It Works |
|-----------|-------------|
| Partial Payment | Enter amount less than residual; invoice stays Open |
| Multiple Payments | Each payment reduces residual until zero |
| Overpayment | Excess becomes a credit note on customer account |

---

## Step 6 — Payment → Bank Reconciliation

### Who
**Accountant** reconciles the payment with the bank statement.

### Procedure

1. **Navigate**: Accounting → Accounting → Bank Reconciliation
   - ![Screenshot Description: Bank Reconciliation dashboard showing two panes — left: "Bank Statement Lines" (unmatched transactions), right: "Matched Items". A search bar and filter options are at the top.]
2. The payment (registered in Step 5) appears as a **matched candidate** on the right pane
   - If the payment was created via "Register Payment", Odoo **automatically pre-reconciles** it with the invoice
3. **Manual Reconciliation** (for direct bank statement imports):
   - A bank statement line (e.g., "Wire transfer from Customer A") appears on the left
   - Drag-and-drop the statement line onto the matching invoice/payment on the right
   - Or click **"Validate"** to accept the suggested match
4. **Reconciliation Result**:
   - The receivable account is fully cleared
   - The bank account balance increases
   - Invoice moves to *Paid & Reconciled* state
   - ![Screenshot Description: After reconciliation — the invoice shows "Fully Paid" status, the payment entry shows "Reconciled" in the Bank Journal.]

### Reconciliation Corner Cases

| Case | Handling |
|------|----------|
| Currency Difference | Odoo auto-calculates exchange rate gain/loss journal entry |
| Bank Fees | Add a "Bank Fees" line in the reconciliation widget |
| Write-Off | Use the "Write-Off" button to write off small differences (< configured tolerance) |

---

## Complete End-to-End Flow Diagram (Text)

```
  CRM                    SALES              INVENTORY            ACCOUNTING
 ┌────────┐         ┌─────────────┐      ┌─────────────┐       ┌──────────────┐
 │  Lead   │───→    │  Quotation   │      │Delivery Order│      │  Draft Invoice│
 │(Draft)  │Qualify │  (Draft)     │      │  (Draft)     │      │  (Draft)      │
 └────────┘         └──────┬──────┘      └──────┬───────┘      └──────┬───────┘
       │                    │                     │                    │
       ▼                    ▼ Confirms?           ▼ Validate?          ▼ Validate?
 ┌──────────┐        ┌──────────────┐      ┌────────────┐       ┌──────────────┐
 │Opportunity│──────→ │  Sales Order  │────→ │   Done     │────→ │   Posted     │
 │(Won)      │Convert │  (Confirmed)  │      │(Delivered) │      │   Invoice    │
 └──────────┘        └──────────────┘      └────────────┘       └──────┬───────┘
                                                                       │
                                                                       ▼
                                                               ┌──────────────┐
                                                               │   Payment    │
                                                               │  Registered  │
                                                               └──────┬───────┘
                                                                      │
                                                                      ▼
                                                               ┌──────────────┐
                                                               │ Reconciled   │
                                                               │ in Bank Stmt │
                                                               └──────────────┘
```

---

## Key Configuration Points

| Setting | Path | Impact |
|---------|------|--------|
| Sales Approval Limit | Sales → Configuration → Settings → Sales → Approval | Total above this = Manager approval needed |
| Product Type | Sales → Products → Product → General Information → Type | Controls whether Delivery Order is created |
| Invoice Policy | Sales → Products → Product → Invoicing → Invoicing Policy | "Ordered quantities" vs "Delivered quantities" |
| Double Validation | Inventory → Configuration → Settings → Operations → Double-Validation | Requires second user to validate picking |
| Bank Reconciliation | Accounting → Configuration → Settings → Reconciliation | Enable / disable auto-reconciliation suggestions |
| Payment Terms | Accounting → Configuration → Management → Payment Terms | Due date calculation on invoices |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Cannot confirm SO | Missing products or customer | Complete all required fields |
| Delivery button not appearing | Product type not "Stockable" | Change product type |
| Invoice button not appearing | Invoice policy = "Delivered" but nothing delivered | Validate delivery first |
| Payment not reconciling | Payment journal ≠ statement journal | Match journals in payment registration |
| Invoice stuck in "Open" | Payment register but not reconciled | Complete reconciliation step |

---

*End of Workflow 01 — Sales to Cash*
