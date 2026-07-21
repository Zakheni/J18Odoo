# Odoo 18 Sales Module — End-User Manual

**Document Version:** 1.0  
**Applies to:** Odoo 18 Community & Enterprise  
**Module:** Sales (`sale`)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Creating Quotations](#2-creating-quotations)
3. [Quotation to Sales Order](#3-quotation-to-sales-order)
4. [Order Management](#4-order-management)
5. [Pricelists](#5-pricelists)
6. [Discounts](#6-discounts)
7. [Delivery](#7-delivery)
8. [Invoicing](#8-invoicing)
9. [Reporting](#9-reporting)
10. [Advanced Features](#10-advanced-features)
11. [Common Workflows](#11-common-workflows)

---

## 1. Overview

The Sales module is the heart of your commercial operations. It manages the end-to-end lifecycle of a sale:

| Stage | Description |
|---|---|
| **Quotation** | A provisional price proposal sent to a customer. No stock impact. |
| **Sales Order** | A confirmed order that reserves stock and triggers downstream operations. |
| **Delivery** | The physical (or digital) shipment of goods to the customer. |
| **Invoicing** | The financial record — an invoice or credit note linked to the order. |

> **Tip:** Use the **Sales Dashboard** as your daily home screen. It shows quotation hit rates, overdue deliveries, and invoicing targets at a glance.

---

## 2. Creating Quotations

### 2.1 From Scratch

1. Go to **Sales → Orders → Quotations**.
2. Click **New**.
3. In the **Customer** field, start typing the customer name. Odoo auto-completes existing contacts from the CRM/contacts database.
   - *If the customer is new:* Type the name and click **Create "…"** or **Quick Create** to add them on the fly.
4. **Quotation Date** defaults to today. Change it if needed.
5. **Expiration Date** is calculated from the customer's pricelist (usually 7–30 days).
6. Add order lines in the **Order Lines** tab:
   - Click **Add a product**.
   - Select a product. The **Description**, **Unit Price**, and **Taxes** are pre-filled from the product form and pricelist.
   - Override the **Quantity**, **Unit Price**, or **Discount** directly in the line.
7. (Optional) Add a **Customer Reference** — useful when the customer provides their own PO number.
8. Click **Save**.

> **⚠️ Warning:** A quotation does NOT reserve stock. Stock is only reserved when the quotation is **confirmed** (converted into a sales order).

### 2.2 From an Opportunity (CRM)

If you use the CRM app:

1. Go to **CRM → Pipeline**.
2. Open an opportunity that is **won** or ready to quote.
3. Click the **Quotation** smart button (top-right).
4. Odoo creates a draft quotation pre-filled with the customer, expected closing date, and any products already listed on the opportunity.
5. Review, adjust quantities/prices, and **Save**.

> **Tip:** You can also create a quotation from an opportunity by clicking the action cog ⚙ → **New Quotation**.

### 2.3 Adding Products

- **Product variants:** When a product has variants (e.g., colour/size), you first choose the product template, then select the specific variant in a second drop-down.
- **Sections & Notes:** Use the **Add a section** or **Add a note** buttons to organise order lines (e.g., grouping hardware vs. software items).
- **Kit/ Bundle products:** If a product is configured as a kit, adding it will explode its components onto the order (see §10.2).

### 2.4 Delivery & Invoicing Addresses

- By default, the **Delivery Address** and **Invoice Address** match the customer's main address.
- To change them, click the pencil icon ✏ next to the address field.
- You can select any contact stored under the customer's company.
- To add a brand-new address on the fly, select **Create a new contact** or **Create a new address**.

> **Tip:** If **Customer → Delivery Address** differ, the system automatically creates a delivery order to the delivery address when the sales order is confirmed.

### 2.5 Payment Terms & Delivery Method

**Payment Terms**  
Set in the **Other Info** tab:

1. Go to the **Other Info** tab on the quotation.
2. **Payment Term**: Select from the drop-down (e.g., *15 Days*, *30% Down + 70% on Delivery*).
3. These terms control the due dates on the customer invoice.

> **⚠️ Warning:** If no payment term is set, the invoice due date will be the invoice date (immediate payment expected).

**Delivery Method**  
1. In the **Other Info** tab, find **Delivery Method**.
2. Select a carrier (e.g., *FedEx*, *In-Store Pickup*).
3. If the delivery method is configured with a **pricelist**, a shipping line is automatically added to the order lines.

---

## 3. Quotation to Sales Order

### 3.1 Confirming (Manually)

1. Open the quotation.
2. Click **Confirm** (top-left button).
3. Odoo does the following automatically:
   - Changes the status from **Quotation** to **Sales Order**.
   - Assigns a sequential order number (e.g., `SO00123`).
   - Reserves stock for each product line (if inventory is tracked in real time).
   - Creates a draft **Delivery Order** (if the products are storable).
   - Creates a draft **Customer Invoice** (if invoicing policy is *Before Delivery* or *On Delivery*).

> **Tip:** If the quotation was sent by email, the confirmation will also update the status in the customer portal.

### 3.2 Sending by Email

1. From the quotation, click **Send by Email**.
2. A template-based email opens with the quotation PDF attached.
3. Edit the subject/body if needed, then click **Send**.
4. The quotation status changes to **Quotation Sent**.
5. Odoo logs the email in the **Chatter** (communication history).

### 3.3 Online Acceptance (Customer Portal)

If **Online Signature** or **Online Payment** is enabled:

1. After sending, the customer receives an email with a secure link.
2. The customer opens the link, reviews the quotation, optionally pays a deposit, and clicks **Accept & Sign**.
3. Odoo automatically confirms the sales order and registers the payment (if any).
4. A signed PDF of the quotation is stored in the Chatter.

> **⚠️ Warning:** Online acceptance only works if the customer has portal access. Check **Settings → Sales → Online Quotations** to enable this feature.

---

## 4. Order Management

### 4.1 Editing a Sales Order

1. Open the sales order.
2. If the order is still a **draft quotation**, edit any field freely.
3. If the order is **confirmed**, most fields are locked. To edit:
   - Click the **Edit** button (pencil icon).
   - You can change quantities, prices, or add/remove lines.
   - Odoo re-computes taxes and totals automatically.
4. Save.

> **⚠️ Warning:** Changing quantities on a confirmed order may affect stock reservations. If stock is insufficient, Odoo will show an under-delivery warning.

### 4.2 Cancelling an Order

1. Open the sales order.
2. Click the action cog ⚙ → **Cancel**.
3. Odoo asks for confirmation. Confirm.
4. The status changes to **Cancelled**.
5. All related deliveries and invoices are also cancelled (if they were still in draft).

> **⚠️ Warning:** Cancelling an order that already has a **validated** delivery or **posted** invoice will leave those documents intact. You must handle them separately (e.g., create a return/credit note).

### 4.3 Locking an Order

Locking prevents any further modification:

1. Open the sales order.
2. Click the lock icon 🔒 (top-right, only visible after confirmation).
3. Once locked, no one can edit lines, confirm new deliveries, or invoice the order.

> **Tip:** Lock orders at the end of the month during the accounting close to prevent accidental changes.

### 4.4 Copying an Order

1. Open the quotation/order you want to duplicate.
2. Click the action cog ⚙ → **Copy**.
3. A new draft quotation opens with all lines pre-filled.
4. Change the customer, dates, or quantities as needed and **Save**.

---

## 5. Pricelists

### 5.1 How Pricelists Work

A **pricelist** defines the selling prices for products. Every order must have a pricelist — by default it is *Public Pricelist* (retail prices).

**Pricelist rules** are evaluated in order of priority (1 = highest):

| Rule Type | Example |
|---|---|
| **Percentage discount** on list price | −10 % |
| **Fixed price** | € 49.99 |
| **Formula based on cost** | Cost × 1.3 |

### 5.2 Applying a Pricelist

1. On the quotation, in the **Other Info** tab, select a **Pricelist**.
2. All line prices automatically recalculate.
3. Pricelists can be set **automatically** per customer (on the contact form: *Sales & Purchase → Pricelist*).

> **Tip:** Use **Pricelist Versions** with date ranges for seasonal or promotional pricing.

### 5.3 Customer-Specific Pricing

1. Go to **Sales → Configuration → Pricelists**.
2. Create a new pricelist (e.g., *VIP Customer Pricing*).
3. Add rules per product, product category, or globally.
4. Assign the pricelist to the customer's contact record.
5. All future quotations for that customer default to this pricelist.

---

## 6. Discounts

### 6.1 Line-Level Discounts

1. On any order line, enter a value in the **Discount (%)** column.
2. The unit price is reduced by the given percentage.
3. The customer's pricelist may already apply a discount — this stacks on top (or replaces it, depending on configuration).

> **⚠️ Warning:** By default, any user can apply a line discount. To restrict discount permissions, go to **Settings → Sales → Discounts** and enable *Allow discounts only with authorization*.

### 6.2 Global (Order-Level) Discounts

Odoo 18 does **not** have a built-in global discount field by default. To apply an across-the-board discount:

- **Option A — Discount line:** Manually add a product named *"Global Discount"* with a negative price (e.g., `−€50.00`).
- **Option B — Pricelist:** Use a pricelist that applies a percentage to all products.

### 6.3 Fixed Discounts

Fixed-amount discounts (e.g., *€10 off*) can be achieved by:

1. Creating a product *"Fixed Discount"* with type **Service**.
2. Adding it as a negative line on the order.
3. Using the **Coupon / Loyalty** program (see §10.5) for automatic fixed discounts at checkout.

> **Tip:** For coupon-based discounts, install the **Coupons & Loyalty** module (`sale_loyalty`).

---

## 7. Delivery

### 7.1 How Delivery Orders Are Created

When a sales order is confirmed:

- **Storable products:** Odoo generates a draft **Delivery Order** (stock picking) for each warehouse and delivery address.
- **Service products:** No delivery order is created.
- **Consumable products:** No delivery order is created (stock is not tracked).

### 7.2 Processing Deliveries

1. Go to **Inventory → Operations → Delivery Orders**.
2. Find the delivery order linked to your sales order (same reference number).
3. Click **Validate** to confirm the goods have shipped.
4. Odoo updates the stock quantity and sets the sales order delivery status to **Done**.

> **⚠️ Warning:** If you validate a delivery with less quantity than ordered, the sales order becomes **Partially Delivered**. You can deliver the remaining items later via the **Backorder** button.

### 7.3 Tracking Shipments

If a **delivery method** with tracking is configured:

1. After validating the delivery, enter the tracking reference in the **Tracking Reference** field.
2. Add the **Tracking URL** (or let Odoo auto-populate it based on the carrier configuration).
3. The customer can click the tracking link from their portal or the email notification.

> **Tip:** Use the **Delivery Status** smart button on the sales order to see real-time tracking.

### 7.4 Partial & Backorders

- **Partial delivery:** Validate only a subset of the lines. Odoo automatically creates a **Backorder** for the remaining items.
- **Backorder:** A new delivery order with the undelivered quantities. Process it just like a regular delivery.

---

## 8. Invoicing

### 8.1 Creating Invoices from Sales Orders

Odoo can invoice:

- **Before delivery** (advance invoice / deposit)
- **On delivery** (invoice when the delivery order is validated)
- **After delivery** (manual trigger)

**To create an invoice:**

1. Open the sales order.
2. Click **Create Invoice**.
3. Choose the invoicing method:
   - *Regular invoice* — invoices all delivered quantities.
   - *Down payment (percentage)* — e.g., 30 % deposit.
   - *Down payment (fixed amount)* — e.g., €500.
4. Click **Create Draft Invoice**.
5. Odoo redirects to the draft invoice in **Accounting**.
6. Review and click **Post** to confirm the invoice.
7. Click **Send & Print** to email the PDF to the customer.

> **Tip:** Use **Invoiceable Lines** smart button to see which order lines are ready for invoicing.

### 8.2 Credit Notes

A credit note reverses an existing invoice:

1. Go to **Accounting → Customers → Invoices**.
2. Open the invoice you need to credit.
3. Click **Add Credit Note**.
4. Choose the reason:
   - *Full refund* — reverses the entire invoice.
   - *Partial refund* — select specific lines.
5. Click **Create Credit Note**.
6. Odoo generates a credit note with negative amounts.
7. Post the credit note. It will reconcile with the original invoice.

> **⚠️ Warning:** A credit note does **not** automatically create a return delivery order. If goods are returned, process the return separately in **Inventory → Operations → Returns**.

### 8.3 Invoicing Policy per Product

Each product can have a different invoicing policy:

- **Ordered quantities** (invoice before delivery)
- **Delivered quantities** (invoice after delivery)

Configure this on the **Product → Invoicing → Invoicing Policy**.

---

## 9. Reporting

### 9.1 Sales Analysis

1. Go to **Sales → Reporting → Sales Analysis**.
2. Use pivot-table-style drag-and-drop to analyse:
   - Total revenue by product, customer, salesperson, or month.
   - Quantity sold.
   - Average price.
3. Apply **Filters** (date range, customer category, etc.).
4. Click **Graph** to switch to bar/line/pie charts.

> **Tip:** Save your favourite views as **Favourites** for quick access.

### 9.2 Margin Analysis

Available when the **Margin** setting is enabled (`Settings → Sales → Margin`):

1. Go to **Sales → Reporting → Margin Analysis**.
2. See **Gross Margin (%)** and **Gross Margin (amount)** per order line or aggregated.
3. Compare actual margin vs. theoretical margin (based on cost price).

> **⚠️ Warning:** Margin accuracy depends on correct **Cost Price** values on the product form. Update cost prices regularly (use periodic inventory valuation).

### 9.3 Dashboard

The **Sales Dashboard** shows key KPIs:

- **Quotation** count and conversion rate.
- **Confirmed orders** this month.
- **To invoice** / **To deliver** orders.
- **Top-selling products**.
- **Salesperson rankings**.

1. Go to **Sales → Dashboard**.
2. Click any KPI tile to drill down into the underlying orders.
3. Use the date range selector (top-right) to view different periods.

---

## 10. Advanced Features

### 10.1 Sales Subscriptions (Recurring)

Requires the **Sales Subscriptions** module (`sale_subscription`).

1. Go to **Sales → Subscription → Subscription Plans** and create a plan (e.g., *Monthly SaaS*).
2. When creating a quotation, select a **Subscription Plan** in the *Other Info* tab.
3. Confirm the order — Odoo automatically generates recurring invoices at the defined interval (weekly, monthly, yearly).
4. Customers can upgrade/downgrade their plan from the portal.

### 10.2 Product Sets / Bundles

Two approaches:

- **Kit (phantom BOM):** Set the product type to **Kit** on the product form. When added to an order, its components are listed as separate lines.
- **Sales Bundles (`product_pack`):** Install the *Product Bundles* module. Create a pack product, and when sold, it shows as a single line but delivers multiple components.

### 10.3 Automatic Workflows

Odoo 18 automates several steps by default:

- **Confirm → Deliver → Invoice** — chain of automatic actions (configurable in **Settings → Sales → Automatic Invoice**).
- **Email confirmation** — auto-sends an order confirmation to the customer.
- **Scheduler actions** — automatically confirm quotations past their expiration date (requires *Sales Automation*).

### 10.4 Sale Order Templates

1. Go to **Sales → Configuration → Sale Order Templates**.
2. Create a template with pre-filled lines, terms, and conditions.
3. When creating a new quotation, select the template in the **Order Template** field.
4. All lines from the template are inserted; adjust quantities as needed.

> **Tip:** Use templates for recurring orders (e.g., monthly office supplies).

### 10.5 Loyalty / Coupon Programs

Requires the **Coupons & Loyalty** module:

1. **Go to** Sales → Configuration → Loyalty Programs.
2. **Create** a program:
   - *Coupon:* Customer enters a code (e.g., `SUMMER20`).
   - *Automatic:* Applied automatically (e.g., *spend €100, get €10 off*).
   - *Next order:* Rewards redeemed on the next purchase.
3. The reward can be a **discount percentage**, **fixed amount**, or **free product**.
4. Customers use the program on the **Sales Order** or in the **Portal**.

> **⚠️ Warning:** Loyalty discounts are calculated **after** line discounts and pricelists. They appear as a separate line on the order.

---

## 11. Common Workflows

### Workflow A: Daily Order Processing

```
1. Check Sales Dashboard
2. Review new quotations → Send email follow-ups
3. Confirm ready-to-close quotations
4. Validate pending delivery orders (Inventory)
5. Create invoices for delivered orders
6. Review overdue invoices (Accounting)
```

### Workflow B: Configure-to-Order (CTO)

```
1. Create quotation from opportunity
2. Select customer-specific pricelist
3. Add configurable product → choose options/variants
4. Set delivery method and payment terms
5. Send quotation for online signature
6. Customer accepts → Order confirmed
7. Manufacturing order created (if product is manufactured)
8. Deliver → Invoice → Collect payment
```

### Workflow C: Returns & Refunds

```
1. Customer requests a return
2. Go to Sales → Orders → Customer Returns
3. Create a return referencing the original sales order
4. Validate the return in Inventory
5. Create Credit Note in Accounting → Invoice → Add Credit Note
6. Reconcile credit note with original invoice
7. (Optional) Process refund payment
```

### Workflow D: Monthly/Quarterly Close

```
1. Ensure all orders are delivered or cancelled
2. Invoice all delivered, non-invoiced orders
3. Post all draft invoices
4. Reconcile payments
5. Lock posted invoices (Accounting → Period Closing)
6. Lock sales orders older than the period
7. Run Sales Analysis report for sign-off
```

---

## Appendix: Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + S` | Save current document |
| `Ctrl + P` | Print / PDF preview |
| `Ctrl + F` | Search (list views) |
| `Alt + N` | Create new record |
| `Alt + E` | Edit current record |

---

*© 2026 — This guide is for training purposes and covers Odoo 18 Sales module features available as of July 2026.*
