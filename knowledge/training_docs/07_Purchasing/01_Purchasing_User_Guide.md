# Odoo 18 Purchasing Module — End-User Guide

> **Document Version:** 1.0  
> **Module:** Purchasing (purchase)  
> **Applies to:** Odoo 18 Community & Enterprise  
> **Audience:** Buyers, Procurement Managers, Accounts Payable teams, Warehouse Operators

---

## Table of Contents

1. [Overview — The Purchase to Pay Cycle](#1-overview--the-purchase-to-pay-cycle)
2. [Getting Started — Configuration & Master Data](#2-getting-started--configuration--master-data)
3. [Creating Purchase Orders (RFQs)](#3-creating-purchase-orders-rfqs)
4. [Confirming Orders & Sending to Suppliers](#4-confirming-orders--sending-to-suppliers)
5. [Receiving Products](#5-receiving-products)
6. [Vendor Bills & Three-Way Matching](#6-vendor-bills--three-way-matching)
7. [Supplier Management](#7-supplier-management)
8. [Purchase Agreements & Contracts](#8-purchase-agreements--contracts)
9. [Purchase Requisitions & Tenders](#9-purchase-requisitions--tenders)
10. [Reporting & Analysis](#10-reporting--analysis)
11. [Tips & Best Practices](#11-tips--best-practices)

---

## 1. Overview — The Purchase to Pay Cycle

The **Purchase to Pay (P2P)** cycle in Odoo 18 covers every step from identifying a need for goods or services through to paying the supplier's invoice. The standard flow is:

```
Need Identified
       │
       ▼
Purchase Requisition (optional)
       │
       ▼
Request for Quotation (RFQ) ──► Vendor Quotation
       │
       ▼
Purchase Order (confirmed)
       │
       ▼
Receipt of Goods (optionally partial)
       │
       ▼
Vendor Bill (matched to PO & receipt)
       │
       ▼
Payment
```

**Key Odoo 18 Concepts:**
- **RFQ / Purchase Order (PO):** A draft document sent to a supplier is a *Request for Quotation*. Once confirmed, it becomes a binding *Purchase Order*.
- **Receipt:** A stock move that records goods physically entering the warehouse.
- **Vendor Bill:** The supplier's invoice; Odoo supports three-way matching (PO ↔ Receipt ↔ Bill).
- **Control State:** When a PO is *locked*, it cannot be modified without explicit unlock.

**Navigation:** `Purchasing → Dashboard`

---

## 2. Getting Started — Configuration & Master Data

### 2.1 Activate the Purchasing App

1. Go to **Apps**.
2. Search for *Purchasing* and click **Activate** (if not already installed).

### 2.2 Configure Settings

Navigate to **Purchasing → Configuration → Settings**.

| Setting | Purpose |
|---------|---------|
| *Products* → *Product Categories* | Define default procurement routes & accounts per category. |
| *Purchase Order* → *Lock Confirmed Orders* | Automatically lock POs after confirmation (recommended). |
| *Purchase Order* → *Send RFQ by Default* | Automate email sending when confirming. |
| *Invoicing* → *Control Policy* | Choose *Based on received quantities* or *Based on ordered quantities*. |
| *Drop Shipping* | Enable direct supplier-to-customer shipments. |
| *Purchase Agreements* | Enable blanket orders, contracts & call-offs. |
| *Purchase Requisitions* | Enable the tendering / bid process. |

### 2.3 Master Data Setup

#### Suppliers

**Purchasing → Vendors → Vendors**

Create each supplier with:
- **Vendor Name**, **Contact**, **Email** (for RFQ automation).
- **Payment Terms** (e.g., Net 30, 2% 10 Net 30).
- **Fiscal Position** (for tax mapping).
- **Purchase Tab:** Default lead time, minimum order quantity, currency.
- **Accounting Tab:** Default expense account, tax rules.

> **Tip:** Use **Vendor Pricelists** (`Vendors → Vendor Pricelists`) to maintain negotiated prices per product. These are automatically applied when creating an RFQ.

#### Products

**Purchasing → Products → Products**

Set up each purchasable product:
1. Product Type: *Stockable Product*, *Consumable*, or *Service*.
2. **Purchase Tab:**
   - *Vendor(s)* — add preferred suppliers with price, lead time, quantity.
   - *Control Policy* — overrides the global setting for this product.
   - *Purchase UoM* — unit of measure used when ordering (e.g., Box of 12).
3. **Inventory Tab:** *Product Category* determines the default expense/income accounts.
4. **Accounting Tab:** *Purchase Account* and *Purchase Taxes*.

---

## 3. Creating Purchase Orders (RFQs)

### 3.1 Manual Creation

1. **Purchasing → Orders → Requests for Quotation** (or click **New** on the dashboard).
2. Fill in the **Vendor** field — Odoo auto-populates payment terms, currency, & fiscal position.
3. Add products in the **Order Lines** tab:
   - **Product** — start typing to search; Odoo pre-fills description, UoM, price from pricelist / product form.
   - **Quantity** — enter the quantity needed.
   - **Unit Price** — override if a one-time negotiated price applies.
   - **Taxes** — adjust if the line requires a different tax treatment.
   - **Delivery Date** — the expected receipt date; Odoo used this for scheduling.
4. Use the **Notes** tab for internal notes (not sent) and **Terms & Conditions** (printed on PO).
5. Click **Save**.

> **Tip:** You can add optional products as separate lines. Use the **Deliveries & Invoices** smart button later to track fulfilment.

### 3.2 Creating from a Purchase Requisition

If a Purchase Requisition has been approved (see Section 9), open the requisition and click **Create Order**. Odoo pre-fills vendor, products, and quantities.

### 3.3 Creating from a Blanket Order / Agreement

See Section 8 — from an agreement, use the **Create Call-off Order** button.

### 3.4 Creating from Sales Order (Drop Shipping)

When a sales order triggers a drop shipment, Odoo auto-creates a PO to the supplier with the customer as the delivery address. No manual action needed unless you need to adjust pricing.

### 3.5 Importing POs (Bulk)

1. **Purchasing → Orders → Requests for Quotation**
2. Click **Favorites → Import Records**.
3. Upload a CSV / Excel file with columns matching the PO fields (vendor, product, quantity, price, etc.).
4. Map columns using the import wizard and validate.

> **Tip:** Download a sample template by clicking the *Download Template* link inside the import wizard.

---

## 4. Confirming Orders & Sending to Suppliers

### 4.1 Confirming an RFQ to a Purchase Order

There are three confirmation methods:

| Action | Button | What Happens |
|--------|--------|--------------|
| *Confirm Order* | **Confirm Order** | Converts RFQ to a confirmed PO. Generates receipt moves (stockable products). Assigns a sequential number. |
| *Send & Print* | **Send & Print** | Opens the email composer, attaches the PDF PO, and optionally confirms on send. |
| *Print* | **Print** | Downloads the PO PDF (A4 / Letter). The RFQ stays as a draft until you click **Confirm Order**. |

### 4.2 The RFQ Email Template

Odoo provides a default *RFQ* email template. You can:

- Edit it in **Settings → Technical → Email → Templates** (technical mode required).
- Customise it per vendor by setting a different email template on the vendor form.
- Manually edit the subject/body in the Send & Print popup before sending.

### 4.3 Order States Explained

| State | Meaning |
|-------|---------|
| **Draft RFQ** | Not yet sent; editable. |
| **Sent** | RFQ sent to vendor; awaiting confirmation response (if vendor confirmed manually). |
| **Purchase Order** | Confirmed. Stock moves generated. Editable only if unlocked. |
| **Locked** | Confirmed + Locked (if setting active). Cannot be modified without unlocking. |
| **Done** | All quantities received. |
| **Cancelled** | Voided — no stock impact. |

### 4.4 Cancelling an Order

Open the PO and click **Cancel**. If receipts or bills exist, you must cancel or delete those first.

> **Warning:** Cancelling a PO does **not** reverse stock moves automatically. You must handle returns separately (see Section 5.4).

---

## 5. Receiving Products

### 5.1 Standard Receipt

Once a PO is confirmed, Odoo generates one or more **Receipts** (stock picking types):

1. **Warehouse → Operations → Receipts**
2. Find the receipt linked to your PO (the *Origin* field shows the PO number).
3. **Validate** the receipt:
   - If full receipt: click **Validate**.
   - If partial: edit quantities on each line, then **Validate**.
4. After validation, the PO's *Received* quantity updates.

Alternatively, you can receive directly from the PO:
- Open the PO → click the **Receipt** smart button → **Validate**.

### 5.2 Over-Receipt

If a supplier sends more than ordered:
- Odoo respects the *Control Policy* setting:
  - *Receive quantities* — you can enter the actual received quantity (no blocking).
  - *Order quantities* — you are blocked from exceeding the ordered quantity.

### 5.3 Backorders

If a partial receipt creates a backorder, Odoo prompts: *Create a backorder?* Click **Create Backorder** to generate a pending receipt for the remaining quantity.

### 5.4 Returns

1. From the receipt, click **Return**.
2. Specify the quantity to return.
3. Choose the reason (optional). Odoo creates a **Return** picking and, if configured, a negative receipt.

### 5.5 Putaway Rules & Locations

If you have multiple storage locations, Odoo applies putaway rules configured in **Inventory → Configuration → Putaway Rules** to determine where received products are stored.

---

## 6. Vendor Bills & Three-Way Matching

### 6.1 Creating a Vendor Bill from a PO

The smoothest method:

1. **Invoicing → Vendors → Vendor Bills → Create**.
2. Set the **Vendor**.
3. In the **Purchase Order** tab, click **Add** and select the PO.
4. Odoo copies PO lines into the bill, respecting the *Control Policy*:
   - *Received quantities* — lines copy only quantities received to date.
   - *Ordered quantities* — lines copy the ordered quantity.
5. Fill in the **Bill Date**, **Due Date**, and **Reference** (supplier invoice number).
6. Click **Validate**.

> **Tip:** You can also create a bill directly from the PO via the **Create Bill** button in the *Invoicing* tab of the PO form.

### 6.2 Three-Way Matching

Odoo 18 validates that:

- **PO Quantity** ≅ **Received Quantity** ≅ **Billed Quantity**

If there is a discrepancy, the invoice status shows a *Matching* alert:

| Status | Meaning |
|--------|---------|
| **Waiting Bills** | No bill created yet. |
| **Waiting Approval** | Bill created but not yet validated. |
| **Invoiced** | Bill validated and matched. |

To review discrepancies:
1. Open the vendor bill → click **Register Payment** or **Action → Check Matching**.
2. Odoo highlights lines where quantities differ.

### 6.3 Landed Costs

For costs that must be distributed across received products (freight, customs, insurance):

1. **Inventory → Operations → Landed Costs** → **Create**.
2. Select the **Receipt** or **PO**.
3. Add the cost line (e.g., Freight = $200).
4. Click **Compute** → Odoo distributes the cost based on weight, volume, or value.
5. **Validate** to update product unit costs.

---

## 7. Supplier Management

### 7.1 Supplier Form

**Purchasing → Vendors → Vendors** — key sections:

| Tab | Fields |
|-----|--------|
| *General* | Name, Address, Website, Tax ID, Tags |
| *Sales & Purchase* | Payment Terms, Fiscal Position, Currency, Supplier Lead Time |
| *Accounting* | Receivable Account, Payable Account, Bank Accounts |
| *Purchase* | Pricelists, Purchase Agreements, Minimal Order Quantity |

### 7.2 Vendor Pricelists

Manage tiered pricing without editing each product:

1. **Purchasing → Vendors → Vendor Pricelists** → **Create**.
2. Select **Vendor** and set **Validity Dates**.
3. Add lines:
   - *Product / Category / Product Template*
   - *Min Quantity*, *Unit Price* (fixed or percentage formula).
   - *Start/End Date* (for seasonal pricing).
4. Save. The pricelist is automatically applied on RFQs.

> **Tip:** Use the *Priority* field to control which pricelist wins when multiple match.

### 7.3 Supplier Info on Products

Each product can have multiple suppliers with different prices, lead times, and minimum quantities:

**Purchasing → Products → Products** → open a product → **Purchase** tab → **Vendors** section.

Click **Add a line** and enter:
- **Vendor**
- **Vendor Product Code** (the supplier's SKU — appears on the PO).
- **Price** (unit price in vendor currency).
- **Lead Time** (days).
- **Min Qty.**

When creating an RFQ for this product, Odoo auto-selects the vendor with the best price that meets the quantity and lead time requirements.

### 7.4 Vendor Blacklist / Blocking

To prevent ordering from a supplier:
- Open the supplier form → **Sales & Purchase** tab → check **Block Purchase**.
- Enter the **Block Reason** (visible to users).
- Blocked suppliers cannot be selected on new POs (existing POs are unaffected).

---

## 8. Purchase Agreements & Contracts

Purchase Agreements (a.k.a. Blanket Orders or Framework Contracts) define long-term terms with a supplier. From an agreement, you create multiple *call-off orders*.

### 8.1 Enabling Purchase Agreements

**Purchasing → Configuration → Settings** → enable **Purchase Agreements**.

### 8.2 Creating an Agreement

1. **Purchasing → Orders → Purchase Agreements** → **Create**.
2. Set:
   - **Supplier**
   - **Agreement Type**: *Purchase Agreement* or *Purchase Contract*.
   - **Quantity / Amount**: total commitment (e.g., 500 units or $10,000).
   - **Validity Dates** — start and end of the agreement.
   - **Payment Terms** (inherit from supplier or override).
3. **Agreement Lines** tab: add products, quantities, and unit prices.
4. Click **Confirm**.

### 8.3 Creating Call-off Orders

From a confirmed agreement:

1. Open the agreement → **Create Call-off Order**.
2. Enter the quantity you want to order now.
3. Odoo creates a draft RFQ pre-filled with the supplier, product, and price.
4. Proceed as normal (Section 3–4).

### 8.4 Tracking Agreement Fulfilment

The agreement form shows:
- *Ordered Quantity* — total from all call-off POs.
- *Invoiced Amount* — sum of validated vendor bills.
- *Remaining* — available balance.

> **Tip:** Use the **Agreement Analysis** report (Section 10) to monitor utilisation across suppliers.

### 8.5 Purchase Contracts (Master Agreements)

If you selected *Purchase Contract* as the agreement type:
- No call-off orders. Instead, you define scheduled deliveries within the contract.
- Odoo auto-generates POs based on the schedule.

---

## 9. Purchase Requisitions & Tenders

Purchase Requisitions allow internal departments to request purchases. Tenders (Call for Bids) send an RFQ to multiple suppliers simultaneously.

### 9.1 Enabling Purchase Requisitions

**Purchasing → Configuration → Settings** → enable **Purchase Requisitions**.

### 9.2 Creating a Purchase Requisition

1. **Purchasing → Orders → Purchase Requisitions** → **Create**.
2. Fill:
   - **Requisition User** — the requester.
   - **Expected Date** — when the items are needed.
   - **Ordering Department** (if departments are enabled).
   - **Product Lines** — product, description, quantity, preferred delivery date.
3. Click **Confirm** to submit for approval.

### 9.3 Approval Workflow

If the *Double Approval* setting is enabled:

1. The requisition moves to *Waiting Approval*.
2. The assigned approver receives a notification.
3. The approver clicks **Approve** or **Refuse**.
4. Once approved, it becomes available for PO generation.

### 9.4 Creating a Tender (Call for Tenders)

1. **Purchasing → Orders → Tenders** → **Create**.
2. Fill in the **Products** (description, estimated quantity).
3. In the **Suppliers** tab, add potential vendors.
4. Click **Send by Email** to invite bids. Each supplier receives an RFQ.
5. When suppliers respond (via portal or email), update the quoted prices on each line.
6. **Compare** offers using the built-in comparison tool:
   - Navigate to **Purchasing → Reporting → Tender Comparison**.
   - Odoo shows a side-by-side table of prices, delivery dates, and total cost.
7. Select the winning bid and click **Create Order** to generate the PO.

> **Tip:** You can also create a tender from a Purchase Requisition using the **Create Tender** button.

---

## 10. Reporting & Analysis

### 10.1 Dashboard Overview

**Purchasing → Dashboard** shows:
- Number of RFQs to send / POs to receive.
- Late receipts.
- Pending approvals.
- Shortcut to create RFQs, agreements, requisitions.

### 10.2 Standard Reports

| Report | Location | Use |
|--------|----------|-----|
| **Purchase Orders Analysis** | Purchasing → Reporting → Purchase Analysis | Pivot / graph by vendor, product, date, category. |
| **Purchase Order Lines** | Purchasing → Reporting → Purchase Order Lines | Detailed line-level data. |
| **Purchase Agreements** | Purchasing → Reporting → Agreement Analysis | Utilisation & spend under agreements. |
| **Vendor Bills Analysis** | Invoicing → Reporting → Vendor Bills Analysis | Spend, outstanding, overdue analysis. |
| **Tender Comparison** | Purchasing → Reporting → Tender Comparison | Compare supplier bids side-by-side. |

### 10.3 Using the Pivot Table

1. Open **Purchase Analysis**.
2. Use the **Measures** dropdown to toggle between:
   - *Quantity Ordered*
   - *Quantity Received*
   - *Quantity Billed*
   - *Unit Price*
   - *Subtotal*
3. Drag dimensions (Vendor, Product Category, Date, Status) into rows/columns.
4. Click **+** to drill down.
5. Click **Insert in Dashboard** to save as a favourite.

### 10.4 Excel Export

In any analysis view:
1. Click **Actions (gear icon) → Export**.
2. Choose *All Data* or *Current View*.
3. Select fields and format (XLSX, CSV).
4. Click **Export**.

> **Tip:** Save custom export presets to reuse for weekly reporting.

### 10.5 Scheduled Reporting

For recurring reports (e.g., weekly pending PO report), use **Settings → Technical → Scheduled Actions** to create an automated email with the report attached. Alternatively, use Odoo's **Spreadsheet** dashboard to build a live-updating report.

---

## 11. Tips & Best Practices

### 11.1 Daily Workflow

1. **Start on the Dashboard** — see at a glance what needs attention (RFQs to send, receipts pending, bills to match).
2. **Process receipts daily** — delayed receipts cause inaccurate stock valuations and mismatched bills.
3. **Match bills on receipt** — create the vendor bill immediately after receipt validation to avoid backlogs.

### 11.2 Avoid Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Forgetting to confirm the RFQ | Enable *Lock Confirmed Orders* — you will notice if it is still editable. |
| Over-receipt blocked | Set *Control Policy* per product to *Receive quantities* if you frequently accept over-deliveries. |
| Duplicate supplier records | Use **Purchasing → Vendors → Vendor Deduplication** (Enterprise feature). |
| Wrong landed cost allocation | Ensure the product category has correct costing method (*Average Cost* or *FIFO*). |
| Bills not matching PO prices | Activate three-way matching and review alerts before validating bills. |

### 11.3 Automation Ideas

- **Auto-confirm RFQs:** Not recommended unless you trust your pricelists 100%.
- **Auto-validate receipts:** Enable *Picking Operations → Validate all receipts automatically* (careful — bypasses quality checks).
- **Email alerts:** Configure *Email aliases* to auto-create RFQs from supplier emails.
- **Scheduler:** Odoo's *Procurement Scheduler* can auto-generate RFQs for products with min/max inventory rules.

### 11.4 Keyboard Shortcuts (Odoo 18 Web)

| Action | Shortcut |
|--------|----------|
| Create new record | `Ctrl + Alt + N` |
| Save | `Ctrl + S` |
| Search | `Ctrl + K` |
| Edit toggle | `Ctrl + E` |
| Discard changes | `Escape` |

### 11.5 When to Use Each Document Type

| Need | Document |
|------|----------|
| One-time buy | RFQ → PO |
| Long-term deal with call-offs | Purchase Agreement |
| Fixed schedule deliveries | Purchase Contract |
| Internal request before procurement | Purchase Requisition |
| Competitive bidding | Tender (Call for Bids) |
| Freight / customs cost distribution | Landed Cost |

---

## Appendix A — Key Fields Reference

| Field | Location | Description |
|-------|----------|-------------|
| *Control Policy* | Product → Purchase Tab | *On ordered quantities* or *On received quantities* for billing. |
| *Minimum Order Quantity* | Vendor Form → Purchase | Blocks RFQ below this qty. |
| *Supplier Lead Time* | Vendor Form → Purchase | Days from order to delivery; used by procurement scheduler. |
| *Vendor Product Code* | Product → Purchase → Vendor Line | Supplier's SKU — printed on PO. |
| *Validation* | PO → *Locked* state | Set via Settings → *Lock Confirmed Orders*. |

## Appendix B — Common Approval Thresholds

Example configuration (set in **Purchasing → Configuration → Settings → Double Approval**):

| Amount Range | Requires Approval |
|--------------|-------------------|
| $0 – $999 | No |
| $1,000 – $9,999 | Department Manager |
| $10,000+ | Director |

---

> **Odoo 18 Purchasing** — Next step: integrate with **Inventory** and **Accounting** modules to close the Purchase to Pay loop.
