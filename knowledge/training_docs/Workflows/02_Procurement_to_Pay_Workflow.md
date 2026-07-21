# 02 — Procurement-to-Pay Workflow (Procure-to-Pay)
**Module**: Purchasing → Inventory → Accounting
**Version**: Odoo 18

---

## Overview

The Procure-to-Pay workflow covers the complete purchasing cycle — from identifying a need for goods/services through to paying the supplier and reconciling the bank statement.

```
Purchasing ──→ Inventory ──→ Accounting ──→ Accounting
Requisition    Receipt         Vendor Bill      Payment
    │              │               │              │
Purchase Order  Validate        Validate      Reconcile
```

### Swimlane — Role Responsibility Matrix

| Step | Requester | Purchase Manager | Inventory User | Accountant / AP | Finance Manager |
|------|-----------|-----------------|----------------|-----------------|-----------------|
| 1. Requisition → PO | Create Requisition | Approve + Confirm PO | — | — | — |
| 2. PO → Receipt | — | — | Receive & Validate | — | — |
| 3. Receipt → Bill | — | — | — | Create & Validate Bill | — |
| 4. Bill → Payment | — | — | — | Register Payment | Approve (if > threshold) |
| 5. Reconciliation | — | — | — | Reconcile | Review |

---

## Step 1 — Purchase Requisition → Purchase Order (PO)

### Who
- **Requester** (any employee with purchasing rights) creates the **Purchase Requisition**
- **Purchase Manager** reviews, approves, and converts it to a **Purchase Order**
- **Purchase Manager** confirms the PO (or it auto-confirms if approval not required)

### Procedure — Purchase Requisition

1. **Navigate**: Purchasing → Orders → Requests for Quotation → Create
   - Or via Purchasing → Orders → Purchase Requisitions → Create (for internal requisition)
   - ![Screenshot Description: RFQ list view — tabs for "Requests for Quotation", "Purchase Orders", "Purchase Requisitions". A blue "Create" button is prominent.]
2. Fill the Requisition:
   - **Vendor**: Select supplier (create new if not exist)
   - **Products**: Add line items
   - **Quantity**, **Unit Price** (or let Odoo suggest from last purchase / pricelist)
   - **Expected Arrival Date**: drives inventory planning
   - **Delivery Address**: default from vendor or override
   - **Order Deadline**: for RFQ responses
3. **Send RFQ** (optional):
   - Click **"Send by Email"** to email PDF to vendor
   - Vendor can respond via portal or email (Odoo can auto-interpret email replies)
4. **Confirm Order**:
   - Click **"Confirm Order"**
   - Status changes: *RFQ* → *Purchase Order*
   - Smart-buttons appear: *Receipt*, *Bill*, *Cancel*
   - ![Screenshot Description: Confirmed PO form — top shows smart-buttons "Receipt" (0 To Do), "Bill" (0 To Do), "Cancel". Status reads "Purchase Order". Below, order lines with confirmed quantities and prices.]

### Approval Workflow

| PO Total | Action Required |
|----------|----------------|
| < Lower Limit | Auto-approved on confirm |
| Between Limits | Manager email notification + approve button |
| > Upper Limit | Double approval (manager + finance) |

Configure at: Purchasing → Configuration → Settings → Purchase Order Approval

### Cross-Module Impact

| Action | Effect |
|--------|--------|
| Confirm PO (stockable product) | Draft Receipt created in Inventory → Operations → Receipts |
| Confirm PO (service product) | No inventory impact; only accounting |
| Confirm PO (consumable) | No receipt needed; consumed on validation |

---

## Step 2 — Purchase Order → Receipt (Inventory)

### Who
**Inventory User** processes the incoming shipment.

### Procedure

1. **Navigate**: Inventory → Operations → Receipts
   - ![Screenshot Description: Receipt list — filter tabs "To Process", "Waiting", "Done". Each line shows Reference (linked to PO), Scheduled Date, Partner, Origin location (Vendor Location).]
2. **Receive Products**:
   - Open the receipt linked to the PO
   - Click **"Validate"** to open the receipt validation wizard
   - The wizard shows:
     - Expected products and quantities (from PO confirmation)
     - Lot/Serial Number fields (if product is tracked)
     - Package fields (if using packages/lots)
     - Destination Location (default: input location → stock)
   - ![Screenshot Description: Validate wizard — product lines with qty to receive, "Done" col checkbox, lot/serial input for each line. Buttons: "Validate", "Scrap", "Return", "Create Backorder".]
3. **Validate the Receipt**:
   - Check quantities received against the PO
   - Modify quantities if partial shipment received
   - Click **"Validate"**
4. **Result**:
   - Status = *Done*
   - Stock on hand for each product increases
   - If partial: Odoo prompts "Create Backorder?" for remaining qty
   - ![Screenshot Description: Receipt in "Done" state — green banner "Incoming Shipment has been validated".]

### Handling Discrepancies

| Issue | How to Handle |
|-------|---------------|
| Quantity mismatch | Edit qty in validate wizard; create backorder if partial |
| Damaged goods | Click "Scrap" during validation to move damaged qty to scrap location |
| Wrong product | Cancel receipt, contact vendor, create return |
| Over-receipt | Configurable tolerance in Product → Inventory tab |

---

## Step 3 — Receipt → Vendor Bill (Accounting)

### Who
**Accountant / AP Clerk** creates and validates the Vendor Bill.

### Procedure

1. **Navigate**: Purchasing → Orders → Purchase Orders → select the delivered PO
2. Click **"Create Bill"** smart-button (appears after receipt is validated)
   - ![Screenshot Description: Bill creation wizard — "Create Bill" with options: "Regular Bill" (based on received qty), "Down Payment". A checkbox "Group by Vendor" for consolidating multiple POs.]
3. Odoo auto-generates a **Draft Vendor Bill** in Accounting → Suppliers → Vendor Bills:
   - Pre-filled from PO:
     - Vendor
     - Bill Reference (can be replaced with vendor's invoice number)
     - Invoice Date
     - Due Date (computed from Payment Terms)
     - Invoice Lines (quantities = received qty, unit price = PO price)
     - Taxes
   - ![Screenshot Description: Draft vendor bill — header shows Vendor, Bill Reference, Invoice Date, Due Date; lines show product, account, quantity, unit price, taxes, subtotal; footer shows totals and tax summary.]
4. **Edit if Needed**:
   - Vendor's actual invoice may differ from PO (e.g., shipping charges, discounts)
   - Add extra lines for:
     - Shipping / handling fees (use a product of type "Service")
     - Discounts (negative line)
     - Withholding tax adjustments
5. **Validate the Bill**:
   - Click **"Validate"**
   - Status: *Draft* → *Posted* (or *Open* in non-ANG accounting)
   - Journal entry:
     | Account | Debit | Credit |
     |---------|-------|--------|
     | Expense / Stock Input (product account) | Cost | — |
     | Tax (input tax account) | Tax Amount | — |
     | Payable (vendor account) | — | Total |

### Matching Bill to Receipt

Odoo performs **3-Way Matching** by default:
1. **Purchase Order** — quantity and price ordered
2. **Receipt** — quantity actually received
3. **Vendor Bill** — quantity and price billed

If mismatch detected: Odoo flags the bill with a warning (e.g., *"Quantity billed exceeds quantity received"*).

---

## Step 4 — Bill → Payment

### Who
**Accountant / AP Clerk** registers the payment. A **Finance Manager** may need to approve if above threshold.

### Procedure

1. **Navigate**: Accounting → Suppliers → Vendor Bills → select the posted bill
   - ![Screenshot Description: Posted vendor bill — status "Posted" with a blue banner. Smart-buttons: "Register Payment", "Send & Print". The residual amount is shown in a colored box.]
2. Click **"Register Payment"**
   - ![Screenshot Description: Payment registration dialog. Fields: Amount (defaults to open balance), Payment Date, Payment Method (Manual, Check, Electronic), Journal (Bank or Cash), Vendor Bank Account, Memo. Checkboxes: "Send Payment Receipt", "Create Payment".]
3. Fill Payment Details:
   - **Amount**: Full balance or partial
   - **Payment Date**: when the payment is made
   - **Payment Method**: Check / Wire Transfer / Manual
   - **Journal**: Bank or Cash account
   - **Vendor Bank Account**: auto-filled if on record
   - **Memo**: reference or notes
4. **Payment Approval** (if enabled):
   - Total > approval threshold → status = *Waiting Approval*
   - Finance Manager: Accounting → Suppliers → Payments → **Approve**
5. Click **"Create Payment"**
6. Result:
   - Payment record in Accounting → Suppliers → Payments
   - Bill status:
     - *Posted* → *Paid* (if fully paid)
     - *Posted* → *Partial* (if partially paid)

### Payment Methods

| Method | Journal | Effect |
|--------|---------|--------|
| Manual | Bank | No automatic bank statement impact |
| Check | Bank Check | Generates check to print |
| Electronic | Bank | Exports payment file (SEPA, NACHA, etc.) |
| Wire Transfer | Bank | Standard bank transfer |

---

## Step 5 — Payment → Bank Reconciliation

### Who
**Accountant** performs the reconciliation.

### Procedure

1. **Navigate**: Accounting → Accounting → Bank Reconciliation
   - ![Screenshot Description: Bank Reconciliation screen — left pane shows unmatched bank statement lines (e.g., "Wire to Vendor X -$500"), right pane lists pending invoices/payments as reconciliation candidates.]
2. **Import Bank Statement** (monthly / manually / automated):
   - Accounting → Accounting → Bank Statements → Import
   - Or via automated CODA/OFX/CSV import
3. **Match Statement Line**:
   - If payment was registered in Step 4: Odoo automatically suggests the match
   - If not yet registered: drag the statement line to the right pane and either:
     - Match to an existing bill & payment
     - Or create a new payment from the statement line directly
   - ![Screenshot Description: Reconciliation matching view — left: bank statement line for -$500; right: the vendor bill and payment are highlighted as a match candidate. A "Validate" button confirms.]
4. **Validate Reconciliation**:
   - Click **"Validate"**
   - Payable account is cleared
   - Bank account reflects the outgoing payment
   - Bill now shows: *Paid & Reconciled*

### Advanced Reconciliation Features

| Feature | Description |
|---------|-------------|
| Auto-Reconcile | Odoo automatically matches statement lines with payments having same reference and amount |
| Write-Off | Small rounding differences (checked in, e.g., $0.02 difference) can be written off automatically |
| Multi-Currency | Exchange rate difference generates a journal entry for the gain/loss |
| Lock Date | Periods can be locked; reconciliation only possible in open / future periods |

---

## Complete End-to-End Flow Diagram (Text)

```
 PURCHASING              INVENTORY                  ACCOUNTING
 ┌──────────┐          ┌──────────────┐          ┌──────────────┐
 │Requisition│          │  Draft Receipt│          │  Vendor Bill  │
 │ (Draft)   │          │  (Waiting)    │          │  (Draft)      │
 └─────┬────┘          └──────┬───────┘          └──────┬───────┘
       │                      │                          │
       ▼ Convert?             ▼ Receive?                 ▼ Validate?
 ┌──────────┐          ┌──────────────┐          ┌──────────────┐
 │  PO       │          │   Done       │          │  Posted      │
 │(Confirmed)│─────────→│  (Received)  │─────────→│  (Open)      │
 └─────┬────┘          └──────────────┘          └──────┬───────┘
       │                                                  │
       │                                                  ▼ Register Payment
       │                                          ┌──────────────┐
       │                                          │   Payment    │
       │                                          │ (Registered) │
       │                                          └──────┬───────┘
       │                                                 │
       │                                                 ▼ Reconcile
       │                                          ┌──────────────┐
       │                                          │ Reconciled   │
       │                                          │ in Bank Stmt │
       └──────────────────────────────────────────┴──────────────┘
```

---

## Key Configuration Points

| Setting | Path | Impact |
|---------|------|--------|
| PO Approval Limits | Purchasing → Configuration → Settings → Purchase Order Approval | Tiers for auto/manual approval |
| 3-Way Matching | Accounting → Configuration → Settings → Vendor Bills → "Bill Matching" | Warns on qty/price mismatches |
| Product Type | Purchasing → Products → Product → General Information | Service products skip receipt |
| Incoterms & Lead Times | Purchasing → Configuration → Settings → Procurement | Drives expected arrival dates |
| Barcode Scanning | Inventory → Configuration → Settings → Barcode | Scan receipts with handheld/scanner |
| Payment Approval | Accounting → Configuration → Settings → Payments | Threshold for payment approval |
| Lock Dates | Accounting → Configuration → Settings → Lock Dates | Prevents changes to locked periods |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Cannot confirm PO | Missing vendor or products | Complete required fields |
| Receipt not appearing | Product type not "Stockable" | Change product type |
| Bill creation disabled | Nothing received yet | Validate receipt first |
| Bill qty > Receipt qty | Mismatch; Odoo warns | Adjust bill qty to match or override with tolerance |
| Payment not matching statement | Different amounts or references | Manually reconcile in bank reconciliation |
| Exchange rate difference | Multi-currency bill/statement | Validate the auto-generated gain/loss entry |

---

*End of Workflow 02 — Procure to Pay*
