# Odoo 18 Inventory — End-User Manual

---

# Table of Contents

1. [Overview](#1-overview)
2. [Warehouse Configuration](#2-warehouse-configuration)
3. [Products](#3-products)
4. [Receiving Stock](#4-receiving-stock)
5. [Delivering Stock](#5-delivering-stock)
6. [Internal Transfers](#6-internal-transfers)
7. [Inventory Adjustments](#7-inventory-adjustments)
8. [Reordering Rules](#8-reordering-rules)
9. [Traceability](#9-traceability)
10. [Reporting](#10-reporting)
11. [Advanced Features](#11-advanced-features)
12. [Common Workflows](#12-common-workflows)

---

# 1. Overview

The Inventory module in Odoo 18 manages the complete lifecycle of stock: from receiving goods from suppliers, through internal storage and transfers, to delivering products to customers.

## 1.1 Key Concepts

| Concept | Description |
|---|---|
| **Warehouse** | A physical or logical location where stock is stored and managed. A company can have multiple warehouses. |
| **Location** | A sub-division within a warehouse (e.g., Shelf A, Row 3, Bin 12). Stock is tracked at the location level. |
| **Stock Move** | A record of product movement between two locations (source → destination). |
| **Quant** | A record showing the quantity of a specific product in a specific location, optionally tracked by lot/serial number. |
| **Inventory Valuation** | The monetary value of stock, calculated using FIFO, Average Cost, or other costing methods. |

## 1.2 Stock Movement Flow

```
Supplier → Receipt → Input Location → Internal Locations → Output Location → Delivery → Customer
                    ↕                              ↕
           Inventory Adjustment          Internal Transfer
```

## 1.3 Enabling the Inventory Module

1. Go to **Apps**.
2. Search for **Inventory**.
3. Click **Activate**.

> 💡 **Tip:** After activation, configure your company's default warehouse settings in **Inventory → Configuration → Settings**.

---

# 2. Warehouse Configuration

## 2.1 Warehouses

A warehouse is the top-level organizational unit for stock.

### Creating a Warehouse

1. Navigate to **Inventory → Configuration → Warehouses**.
2. Click **Create**.
3. Fill in the fields:

   | Field | Description |
   |---|---|
   | **Warehouse Name** | A unique, descriptive name (e.g., "Main Warehouse – Chicago") |
   | **Short Name** | An abbreviation used in internal reference codes (e.g., "CHI") |
   | **Address** | The physical address of the warehouse |
   | **Company** | The legal entity that owns the warehouse |
   | **Resupply From** | If set, this warehouse is replenished from another warehouse |

4. Configure the **Warehouse Configuration** tab:
   - **Storage Locations**: Enable to use sub-locations within this warehouse.
   - **Multi-Warehouses**: Enable when operating more than one warehouse.
   - **Manage Packages**: Enable for package-level tracking.
   - **Lots & Serial Numbers**: Enable for traceability.
   - **Expiry Dates**: Enable for perishable or dated products.

5. Set the default **Location Types**:
   - **Input Location** — Where received goods are initially placed.
   - **Quality Control Location** — Where goods awaiting inspection are held.
   - **Output Location** — Where picked goods are staged before delivery.
   - **Pack Location** — Where picked products are packed into boxes/crates.
   - **Production Location** — Where manufacturing consumes/produces stock.

6. Click **Save**.

> 💡 **Tip:** Each warehouse automatically creates a location hierarchy when "Storage Locations" is enabled. The parent location shares the warehouse name.

## 2.2 Locations

Locations are the finest granularity of stock tracking.

### Creating a Location

1. Navigate to **Inventory → Configuration → Locations**.
2. Click **Create**.
3. Fill in these critical fields:

   | Field | Description |
   |---|---|
   | **Name** | Descriptive name (e.g., "Row A – Shelf 3") |
   | **Parent Location** | The broader location this belongs to |
   | **Location Type** | `Physical`, `Customer`, `Supplier`, `Production`, `Inventory Loss`, `View` |
   | **Warehouse** | The warehouse this location belongs to |
   | **Barcode** | Scannable identifier |
   | **Removal Strategy** | `FIFO`, `LIFO`, or `Closest` — used during picking |
   | **Put-Away Strategy** | `None` or a custom put-away rule |

4. Click **Save**.

### Location Types Explained

| Type | Usage |
|---|---|
| **Physical** | Standard storage shelves, bins, racks |
| **Customer** | Virtual location for delivered stock (do not put physical products here) |
| **Supplier** | Virtual location for incoming goods before receipt is validated |
| **Production** | Used in manufacturing for work-in-progress |
| **Inventory Loss** | System location for scrapped/lost goods |
| **View** | A group/category for organizing other locations |

### Removal Strategies

- **FIFO** (First In, First Out): The oldest stock is picked first. Best for perishable goods.
- **LIFO** (Last In, First Out): The newest stock is picked first.
- **Closest**: Picks from the location with the shortest travel distance.

> 💡 **Tip:** Use **FIFO** as your default removal strategy for most warehouses — it matches standard accounting practice and reduces expiry risk.

## 2.3 Storage Categories

Storage categories allow you to group locations by physical characteristics (size, weight limit, temperature zone).

### Creating a Storage Category

1. Navigate to **Inventory → Configuration → Storage Categories**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Name** | e.g., "Cold Storage", "Pallet Racking", "Small Bins" |
   | **Allow New Product** | Can products be placed here during put-away? |
   | **Capacity** | Maximum weight or volume |
   | **Parent Category** | For hierarchy (e.g., "Freezer" under "Cold Storage") |

4. Assign the category to one or more **Locations** via the location form.
5. Click **Save**.

## 2.4 Routes & Push/Pull Rules

Routes define how products move through the supply chain. Each route contains one or more **push** or **pull** rules.

### Creating a Route

1. Navigate to **Inventory → Configuration → Routes**.
2. Click **Create**.
3. Fields:

   | Field | Description |
   |---|---|
   | **Route Name** | e.g., "Buy → Stock", "Customer Shipping" |
   | **Company** | Restrict to one company (multi-company setups) |
   | **Active** | Enable/disable without deleting |
   | **Product Selection** | Apply to product categories or individual products |

4. Add **Rules**:
   - **Pull Rule**: Creates a need upstream (e.g., a sale triggers a purchase).
   - **Push Rule**: Propagates stock downstream (e.g., received goods are automatically moved to storage).
   - **Operation Type**: Receipt, Delivery, Internal Transfer, etc.
   - **Source Location / Destination Location**.
   - **Lead Time** (days) for planning.
   - **Procurement Group** for grouping moves.

5. Click **Save**.

> 💡 **Tip:** The default "Buy" route is: Buy Products → Vendor → Receipt → Input → Storage. The default "Manufacture" route is: Production → Storage. Both are pre-configured and ready to use.

---

# 3. Products

## 3.1 Creating a Product

1. Navigate to **Inventory → Products**.
2. Click **Create**.
3. **General Tab**:

   | Field | Description |
   |---|---|
   | **Product Name** | The display name for internal and external use |
   | **Can Be Sold** / **Can Be Purchased** | Determines product type visibility |
   | **Product Type** | `Stockable Product`, `Service`, `Consumable` |
   | **Internal Reference** | Your internal SKU or part number |
   | **Barcode** | UPC, EAN, or custom barcode |
   | **Unit of Measure** | See §3.3 |
   | **Product Category** | See §3.4 |

4. **Inventory Tab**:

   | Field | Description |
   |---|---|
   | **Routes** | Which routes apply (e.g., Buy, Manufacture, Dropship) |
   | **Hazards** | Dangerous goods classification (if applicable) |
   | **Expiry Date** | Enable for date-tracked products |
   | **Storage Category** | Limit where this product can be stored |

5. **Sales / Purchase Tabs**: Set prices, supplier info, customer lead times.
6. Click **Save**.

> ⚠️ **Important:** A **Stockable Product** tracks inventory quantities. A **Consumable** tracks availability but not valuation. A **Service** is never stocked.

## 3.2 Product Variants

Use **Variants** when a product has multiple options (e.g., T-Shirt in Small/Medium/Large, Red/Blue/Green).

### Creating Variants

1. Go to **Inventory → Products** and open a product.
2. Click the **Attributes & Variants** tab.
3. Click **Add a line** under **Attribute Lines**.
4. Select or create an **Attribute** (e.g., "Size", "Color").
5. Add **Values** (e.g., "S", "M", "L").
6. Odoo automatically generates all variant combinations.
7. Optional: Set a **Price Extra** per value (e.g., "XL size +$5.00").
8. Click **Save**.

Each variant appears as a separate product record in the product list. You can set barcodes, weights, and images per variant.

> 💡 **Tip:** Use the **Product Variant Configurator** (a wizard) when you need to create variants in bulk with detailed per-variant settings.

## 3.3 Units of Measure (UoM)

### Categories

UoMs are organized into categories. Products in the same category can be converted automatically.

| Category | Examples |
|---|---|
| **Unit** | Unit, Dozen, Pair, Each |
| **Weight** | kg, g, lb, oz |
| **Volume** | L, mL, gal |
| **Length** | m, cm, ft, in |

> ⚠️ **Important:** A product's **UoM** cannot be changed after the first stock move. Choose carefully during setup.

### Creating a New UoM

1. Navigate to **Inventory → Configuration → Unit of Measure**.
2. Click **Create**.
3. Fill in:

   | Field | Description |
   |---|---|
   | **Unit of Measure** | Name, e.g., "Pallet" |
   | **Category** | Must match related UoMs |
   | **Ratio** | Conversion factor (e.g., 1 Pallet = 50 Units) |
   | **Rounding Precision** | How many decimal places to allow |

4. Click **Save**.

> 💡 **Tip:** Set the rounding precision carefully. Too many decimals can cause rounding errors in inventory valuation.

## 3.4 Product Categories

Product categories control accounting, route defaults, and property inheritance.

### Creating a Product Category

1. Navigate to **Inventory → Configuration → Product Categories**.
2. Click **Create**.
3. Fields:

   | Field | Description |
   |---|---|
   | **Name** | e.g., "Electronics", "Raw Materials" |
   | **Parent Category** | For tree hierarchy |
   | **Properties** | Force specific routes, costing method, or account settings for all products in this category |

4. Click **Save**.

### Costing Methods

Set on the Product Category (or overridden per product):

| Method | Description |
|---|---|
| **Standard Price** | A fixed cost you set manually. Simple but may not reflect true cost. |
| **Average Cost (AVCO)** | Weighted average of all purchase costs. Updated on every receipt. |
| **FIFO** | Tracks cost by individual purchase batches. First in = first out for costing. |

> 💡 **Tip:** Most companies use **AVCO** or **FIFO**. FIFO is more accurate but requires lots/serial tracking if you want physical FIFO too.

## 3.5 Barcodes

### Assigning Barcodes

1. Open a product (or variant).
2. In the **General** tab, enter the **Barcode** field.
3. Common formats:
   - **EAN-13** (13 digits) — standard retail barcode
   - **UPC-A** (12 digits) — North America retail
   - **Code 128** — flexible alphanumeric
   - **GS1-128** — used for logistics labels

### Scanning Workflow

1. Ensure a barcode scanner is connected in keyboard-wedge (HID) mode.
2. In any Inventory screen, click into the barcode field.
3. Scan the barcode.
4. Odoo auto-fills the product and quantity.

> 💡 **Tip:** Odoo 18 supports **GS1 barcode parsing** — one barcode can encode product ID, quantity, lot number, and expiry date. Enable in **Settings → Barcode → GS1 Barcode Support**.

---

# 4. Receiving Stock

## 4.1 Purchase Receipts

### Standard Receiving Workflow

**Precondition:** A Purchase Order (PO) has been confirmed with a supplier.

1. **Trigger the Receipt**:
   - The system automatically creates a **Receipt** when the PO is confirmed.
   - Alternatively, navigate to **Inventory → Operations → Receipts**.

2. **Open the Receipt**:
   - Find the receipt linked to your PO.
   - The receipt is in **Draft** or **Waiting** state.

3. **Validate Quantities** (if different from the PO):
   - Click the product line.
   - Adjust the **Done** quantity to reflect what physically arrived.

4. **Assign Lots/Serial Numbers** (if enabled):
   - In the **Lot/Serial Number** column, click **Add a line**.
   - Enter or scan each lot number and quantity.

5. **Validate the Receipt**:
   - Click **Validate**.
   - The stock is moved from the Supplier Location to the Input Location.
   - If connected, the PO is marked as "Received".

> ⚠️ **Warning:** Validating a receipt updates inventory valuation in real time (for AVCO/FIFO). Verify quantities carefully before validation.

### Partial Receiving

1. Open the receipt.
2. Enter the quantity actually received in the **Done** column.
3. Click **Validate**.
4. Odoo creates a **Backorder** for the remaining quantity automatically.
5. Use the backorder to receive the rest later.

## 4.2 Put-Away Strategies

Put-away strategies automatically suggest where to store received products.

### Creating a Put-Away Rule

1. Navigate to **Inventory → Configuration → Put-Away Rules**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Product** | Specific product (or leave empty for all products) |
   | **Source Location** | Where the product comes from (e.g., Input) |
   | **Destination Location** | Where to store it |
   | **Sequence** | Order of evaluation (lower number = higher priority) |
   | **Storage Category** | Restrict by category |
   | **Package Type** | Restrict by packaging |

4. Click **Save**.

### How Put-Away Works

When you validate a receipt with a put-away rule:
1. The system checks the product against all rules (sorted by sequence).
2. The first matching rule determines the destination.
3. The stock move's destination is automatically updated before validation.

> 💡 **Tip:** Use sequence values 1, 10, 20, 30 to leave room for inserting rules later.

## 4.3 Quality Checks at Receipt

Odoo 18 includes quality control (QC) workflows that can be triggered automatically during receiving.

### Setting Up QC Points

1. Navigate to **Inventory → Configuration → Quality Control Points**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Title** | e.g., "Incoming Inspection – Electronics" |
   | **Product** | Specific product or leave blank for all |
   | **Operation** | `Receipt` — triggers after receipt validation |
   | **Team** | QC team responsible |
   | **Test Type** | See below |
   | **Measure on** | `Percent` or `Units` |

4. **Test Types**:
   - **Pass/Fail** — Simple yes/no check.
   - **Measure** — Record a numeric value (e.g., weight, voltage).
   - **Take Photo** — Capture an image for later review.

5. Click **Save**.

When the receipt is validated, Odoo automatically creates a **Quality Check** task. Complete it in **Inventory → Quality → Quality Checks**.

### Two-Step Receiving (QC Hold)

1. Enable **Storage Locations** in warehouse settings.
2. Create a **Quality Control location** (type: Physical).
3. Receiving moves stock: **Supplier → QC Location**.
4. After QC passes, move stock: **QC Location → Storage** (via an internal transfer).

---

# 5. Delivering Stock

## 5.1 Delivery Orders

### Standard Delivery Workflow

**Precondition:** A Sales Order (SO) has been confirmed.

1. Navigate to **Inventory → Operations → Delivery Orders**.
2. Find the delivery order linked to your SO.
3. The delivery is in **Waiting** state until the products are available.

### Picking Operations

**One-Step Delivery** (direct ship):

1. Open the delivery order.
2. Click **Check Availability**:
   - Odoo reserves stock from the available quants.
   - If insufficient stock, the delivery stays in **Waiting** or **Partially Available** status.

3. **Reserve More** (if needed):
   - Click the **ⓘ** icon next to a product line.
   - View detailed quant information.
   - Manually assign lots if auto-reservation is not desired.

4. Enter exact **Done** quantities (if different from ordered).
5. Assign **Lot/Serial Numbers** if required.
6. Click **Validate**.
7. Stock is removed from your inventory and moved to the **Customer** location.

> 💡 **Tip:** Use the **Check Availability** button daily during your morning workflow to see which orders are ready and which are delayed.

## 5.2 Multi-Step Delivery

### Three-Step Delivery (Pick → Pack → Ship)

1. **Warehouse Configuration** → Set **Outgoing Shipments** to `Pack products then ship (3 steps)`.
2. The system now creates three operations for each delivery:
   - **Pick**: Move stock from storage to the **Pick/Pack** location.
   - **Pack**: Move from **Pick/Pack** to **Output** (user scans packed boxes).
   - **Ship**: Move from **Output** to **Customer**.
3. Each step must be validated in sequence.

> 💡 **Tip:** Multi-step delivery improves accuracy for high-volume operations. Each step can have separate barcode scanning and QC checks.

### Two-Step Delivery (Pick → Ship)

1. **Warehouse Configuration** → Set **Outgoing Shipments** to `Pick products then ship (2 steps)`.
2. Operations: **Pick** (storage → output) → **Ship** (output → customer).

### Printing a Picking Report

1. Open a delivery order.
2. Click **Print → Delivery Slip**.
3. Options:
   - **Picking Operations** — list of products to pick.
   - **Package Label** — GS1-128 label for logistics.
   - **GSP (Global Standard 1)** labels for transport.

## 5.3 Shipping Methods

1. Navigate to **Inventory → Configuration → Shipping Methods**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Name** | e.g., "UPS Ground", "FedEx Express" |
   | **Provider** | UPS, FedEx, USPS, DHL, or generic |
   | **Website** | Show on checkout? |
   | **Price Rule** | Fixed price, or formula based on weight/subtotal |
   | **Integration** | Configure API keys for real-time rates and label printing |

> 💡 **Tip:** Odoo 18 supports **live shipping rates** from UPS, FedEx, DHL, and USPS. Install the corresponding connector module from Apps.

## 5.4 Batch Picking

Batch picking groups multiple pickings into one efficient route.

### Creating a Batch

1. Navigate to **Inventory → Operations → Batch Picking**.
2. Click **Create**.
3. Click **Add Picks** and select the individual pickings.
4. Alternatively, set **Batch Picking** to `Auto` in **Settings** for automatic batch creation when pickings are confirmed.

5. **Batch Picking View**:
   - Products are consolidated across all picks.
   - Pickers see total quantities needed per product.
   - When a product is picked, it's assigned to the original deliveries proportionally.

6. Validate the batch: **Mark as Done**.

> 💡 **Tip:** Use **Batch Picking** for e-commerce operations where you pick 50+ orders per day. It reduces travel time significantly.

---

# 6. Internal Transfers

## 6.1 Creating an Internal Transfer

Use internal transfers to move stock between locations within the same warehouse or between warehouses.

1. Navigate to **Inventory → Operations → Internal Transfers** (or **Operations → Transfers**).
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Source Location** | Where the stock is now |
   | **Destination Location** | Where the stock should go |
   | **Scheduled Date** | When the move should occur |
   | **Company** | For inter-company transfers |

4. **Operations** tab — Add products and quantities.
5. Click **Check Availability** to reserve.
6. Click **Validate** to execute.

> 💡 **Tip:** Internal transfers update the **moves** without journal entries — the stock value is preserved if both locations belong to the same company and valuation method.

## 6.2 Inter-Warehouse Transfers

1. Ensure both warehouses are configured under **Warehouses**.
2. Create a **Route** for inter-warehouse transfers (e.g., "Chicago → Dallas").
3. Create an internal transfer:
   - Source: **Chicago/Stock**
   - Destination: **Dallas/Input**
4. Validate.

5. The receiving warehouse can then perform its own put-away from Input to Stock.

> 💡 **Tip:** For recurring transfers, create a **Reordering Rule** (see §8) that triggers automatic replenishment between warehouses.

---

# 7. Inventory Adjustments

## 7.1 Physical Inventory Counts (Cycle Counts / Full Counts)

### Creating an Inventory Adjustment

1. Navigate to **Inventory → Operations → Inventory Adjustments**.
2. Click **Create**.
3. Choose **Scope**:
   - **Whole Warehouse** — Count everything.
   - **One Product** — Count a single item.
   - **One Location** — Count all items in a specific location.
   - **One Storage Category** — Count all products in a category.

4. **Set Initial Count**:
   - Click **Add Products** and select products.
   - Optionally, click **Start Inventory** to lock stock and prevent movement during counting (for full accuracy).

5. **Enter Counted Quantities**:
   - For each line, change **Counted Quantity** from "0" to what you physically counted.
   - Use **Scan Barcode** for rapid entry.
   - Tap **Tab** to auto-confirm and move to the next line.

6. Click **Apply All** to post the adjustment.
   - Odoo creates inventory moves to correct any discrepancies.
   - A journal entry is generated for valuation impact.

> ⚠️ **Warning:** Applying an adjustment immediately affects valuation. Always have a second person verify counts for high-value items.

### Cycle Counting (Ongoing)

Use cycle counts for regular verification without taking a full inventory.

1. **Inventory → Configuration → Cycle Counts** (if not visible, enable feature in Settings).
2. Set up cycles: A-items daily, B-items weekly, C-items monthly.
3. The system creates suggested counts based on your schedule.
4. Complete them as standard Inventory Adjustments.

> 💡 **Tip:** Run cycle counts on your top 20% of products (by value) every week — this covers ~80% of your inventory value.

## 7.2 Scrapping Products

Use the **Scrap** operation to remove damaged, expired, or obsolete stock.

1. Navigate to **Inventory → Operations → Scrap**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Product** | The item to scrap |
   | **Quantity** | How many |
   | **Lot/Serial** | (if tracked) |
   | **Source Location** | Where the product is now |
   | **Scrap Location** | Usually "Inventory Loss" (system creates this) |

4. Click **Validate**.
5. The product is moved to the **Inventory Loss** location.
6. A journal entry is created debiting the loss account and crediting the inventory account.

> 💡 **Tip:** Use the **Reason** field to document why stock was scrapped — this helps with trend analysis and loss prevention.

---

# 8. Reordering Rules

## 8.1 Creating a Reordering Rule

Reordering rules automate replenishment — when stock drops below a minimum, Odoo creates a procurement (purchase order or internal transfer).

1. Navigate to **Inventory → Operations → Reordering Rules**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Product** | The product to replenish |
   | **Warehouse** | Replenish this warehouse |
   | **Location** | Destination location within the warehouse |
   | **Route** | `Buy` (purchase) or another route |

4. **Trigger** section:

   | Field | Description |
   |---|---|
   | **Min Quantity** | When forecasted stock drops below this, a procurement is triggered |
   | **Max Quantity** | The target quantity to replenish to |
   | **Multiple Quantity** | Buy in multiples of this (e.g., 10 = order in boxes of 10) |

5. **Timing** section:

   | Field | Description |
   |---|---|
   | **Lead Time** | Days between order and receipt |
   | **Order Frequency** | Days between orders (to avoid ordering too often) |

6. Click **Save**.

### How It Works

1. The **Procurement Scheduler** runs automatically at intervals (or on demand).
2. For each product, the scheduler calculates **Forecasted Quantity** = On Hand − Outgoing + Incoming.
3. If Forecasted Quantity < **Min Quantity**, a procurement is triggered for `Max − Forecasted` (rounded to nearest Multiple Quantity).
4. The procurement goes through the configured **Route** (Buy → PO, Manufacture → MO, etc.).

> 💡 **Tip:** The procurement scheduler can be run manually from **Inventory → Operations → Run Scheduler** to test your rules.

## 8.2 Min/Max Rules in Practice

### Example: "USB-C Cables"

| Setting | Value | Reasoning |
|---|---|---|
| Min Quantity | 100 | Safety stock for 5 days |
| Max Quantity | 500 | 25 days of demand |
| Multiple Quantity | 50 | Supplier sells in packs of 50 |
| Lead Time | 7 days | Supplier lead time |
| Order Frequency | 14 days | Order every 2 weeks |

**When it triggers:** If forecasted stock = 80 (< 100), Odoo proposes buying 420 units (500 − 80, rounded up to 450 to meet multiple of 50).

### Using Vendor Lead Times

Reordering rules respect the **Supplier Lead Time** (days) configured on the product's Purchase tab. The scheduler calculates:

- **Order Date** = Expected Shortage Date − Lead Time

> 💡 **Tip:** When products are purchased from multiple vendors, the default vendor (first in the list) is used. Vendor-specific lead times are respected.

## 8.3 Managing Reordering Rules

### Viewing Pending Procurements

1. Open the **Reordering Rule**.
2. The **Messages** tab shows:
   - "Procurement created on [date]."
   - Links to the resulting Purchase Order.

3. Use the **Run Scheduler** button to force a review.

### Disabling a Rule Temporarily

1. Open the rule.
2. Uncheck **Active**.
3. Click **Save**.
4. The rule will be skipped on the next scheduler run.

> 💡 **Tip:** Never delete a reordering rule — deactivate it. This preserves the historical data and allows easy reactivation.

---

# 9. Traceability

## 9.1 Lots & Serial Numbers

### Enabling Lot/Serial Tracking

1. **Inventory → Configuration → Settings**.
2. Scroll to **Traceability**.
3. Enable **Lots & Serial Numbers**.
4. Choose:
   - **Use Lots** (groups of products, e.g., production batch)
   - **Use Serial Numbers** (unique per single item)

### Assigning Lots at Receipt

1. Open the receipt.
2. In the product line, expand **Lot/Serial Number**.
3. Click **Add a line**.
4. Enter the Lot number (or click **Generate** to auto-create).
5. Enter the quantity for this lot.
6. Repeat for additional lots.
7. Validate the receipt.

### Assigning Serial Numbers at Receipt

1. Open the receipt.
2. In the product line, expand **Lot/Serial Number**.
3. Click **Add a line**.
4. Enter or scan each individual serial number.
5. The system tracks each unit uniquely.

## 9.2 Expiry Dates

### Setting Up Expiry Tracking

1. **Inventory → Configuration → Settings** → **Traceability**.
2. Enable **Expiration Dates**.
3. **Products** → Open the product → **Inventory** tab.
4. Enable **Expiration Date**.
5. Configure:

   | Field | Description |
   |---|---|
   | **Product Life** | Total lifespan (days) from production |
   | **Shelf Life** | How long it can sit on the shelf after receipt |
   | **Alert When Expires** | Days before expiry to trigger a notification |
   | **Use Dates** | Best-before or use-by (days) |

### Working with Expired Stock

1. **Inventory → Reporting → Expiration Alerts**.
2. Products approaching expiry are highlighted.
3. Options:
   - **Move to discount zone** (internal transfer) for quick sale.
   - **Scrap** (if fully expired).
   - **Quarantine** move to a hold location.

## 9.3 Traceability Reports

### Lot Traceability Report

1. Navigate to **Inventory → Reporting → Traceability Report**.
2. Select a **Lot** or **Serial Number**.
3. The report shows a tree:

   ```
   Supplier → Receipt (lot assigned)
   → Move to Storage (internal)
   → Delivery 001 (to Customer A)
   → Delivery 002 (to Customer B)
   → Scrap (Qty 1 damaged)
   ```

4. Use the **Forward / Backward** traceability buttons:
   - **Forward**: Where did this lot go?
   - **Backward**: Where did this lot come from?

### Product Traceability

1. **Inventory → Reporting → Product Moves**.
2. Filter by product and date range.
3. See each stock move in/out for that product.

> 💡 **Tip:** Use the **Traceability Report** during a product recall. Enter the lot number and instantly see which customers received affected units.

---

# 10. Reporting

## 10.1 Inventory Analysis

1. Navigate to **Inventory → Reporting → Inventory Analysis**.
2. This is a **pivot table** view. Drag fields to rows/columns:

   | Field | Purpose |
   |---|---|
   | **Product** | See quantities per product |
   | **Location** | Filter by storage location |
   | **Date** | Trend over time |
   | **Lot/Serial** | Traceability breakdown |

3. **Measures**:
   - **Quantity** (On Hand)
   - **Forecasted Quantity**
   - **Incoming** (over selected period)
   - **Outgoing** (over selected period)
   - **Days of Stock** (stock / average daily usage)
   - **Inventory Value** (sum of product cost × qty)

4. Use **Filters**:
   - **Products at Risk** — Products below min quantity.
   - **Slow Movers** — Products with no movement in 90 days.
   - **ABC Analysis** — Top-value products.

> 💡 **Tip:** Save your most-used pivot table as a **Favorite** (click the star icon) for one-click access.

## 10.2 Valuation Reports

1. Navigate to **Inventory → Reporting → Inventory Valuation**.

   | Column | Meaning |
   |---|---|
   | **Product** | Product name |
   | **Quantity** | On-hand units |
   | **Unit Cost** | Cost per unit (based on costing method) |
   | **Total Value** | Quantity × Unit Cost |
   | **Location** | Where the stock is held |

2. Click any **Total Value** cell to drill down into the underlying valuation layers (FIFO) or journal entries.

### Inventory Valuation Journal

1. **Invoicing → Accounting → Journal Entries**.
2. Filter by **Inventory Valuation** or **Inventory Adjustments**.
3. Each entry shows:
   - **Debit**: Inventory Asset account.
   - **Credit**: Counterpart account (Stock Input / Output / Interim).

> 💡 **Tip:** Run the **Inventory Valuation** report at month-end before closing the books. It should match your general ledger inventory account.

## 10.3 Movement History

1. Navigate to **Inventory → Reporting → Moves History** (or **Product Moves**).
2. Filter by:
   - **Date range**
   - **Product**
   - **Reference** (PO, SO, internal)
   - **Location**

3. Each row shows:
   - Date & time
   - Product & quantity
   - Source → Destination
   - Reference document
   - Lot/Serial number

4. **Export** to Excel via the **📥** button for further analysis.

## 10.4 Stock Forecast Report

1. **Inventory → Reporting → Stock Forecast**.
2. Shows projected inventory over time based on:
   - Current stock
   - Open purchase orders (incoming)
   - Open sales orders (outgoing)
   - Manufacturing orders (incoming and outgoing)
   - Reordering rule lead times

3. Useful for:
   - Anticipating stockouts
   - Planning purchase dates
   - Communicating with suppliers

> 💡 **Tip:** Use the **Stock Forecast** during weekly planning meetings to discuss upcoming shortages with the purchasing team.

---

# 11. Advanced Features

## 11.1 Batch Picking

Refer to [§5.4 Batch Picking](#54-batch-picking) for the primary guide.

### Wave Picking (Advanced Batch)

1. Enable **Batch Picking** in Settings.
2. Configure **Wave Rules** in **Inventory → Configuration → Batch Picking Waves**.
3. Waves can filter by:
   - **Delivery Method** — All UPS orders.
   - **Cutoff Time** — Orders before noon.
   - **Carrier** — All FedEx ground.
4. When triggered, the system creates a batch picking for all qualifying deliveries.

## 11.2 Dropshipping

Dropshipping sends products directly from the supplier to the customer — your warehouse never touches the goods.

### Enabling Dropshipping

1. **Inventory → Configuration → Settings**.
2. Under **Operations**, enable **Dropshipping**.
3. Create a **Dropship Route** (or use the pre-built one).

### Using Dropshipping

1. Create a **Sales Order** for your customer.
2. On the product line, set the **Route** to **Dropship**.
3. Confirm the Sales Order.
4. A **Purchase Order** is automatically created with:
   - Supplier = your vendor.
   - Delivery Address = your customer's address.
5. Confirm the PO.
6. The supplier ships directly to the customer.

> 💡 **Tip:** Dropshipping works best with products marked as "Can Be Sold" and "Can Be Purchased" with a supplier linked. No inventory is tracked for these products.

### Drop Shipping (Multi-Warehouse Variation)

If you have multiple warehouses:
1. Create a **Reordering Rule** with route **Buy → Dropship**.
2. When stock is low, automatically trigger a dropship PO.
3. The customer's delivery address is taken from the sales order.

## 11.3 Landed Costs

Landed costs add extra expenses (freight, insurance, customs) to the product's cost for accurate valuation.

### Recording Landed Costs

1. Navigate to **Inventory → Operations → Landed Costs**.
2. Click **Create**.
3. Configure:

   | Field | Description |
   |---|---|
   | **Document Number** | Customs doc or freight bill reference |
   | **Date** | Date of cost incurrence |
   | **Picking List/Picking** | Select the receipt these costs apply to |

4. **Cost Lines** tab:

   | Field | Description |
   |---|---|
   | **Product** | The service/expense (e.g., "Shipping Freight") |
   | **Amount** | Total cost |
   | **Split Method** | `Equal`, `By Quantity`, `By Volume`, `By Weight` |

5. Click **Validate**, then **Post Journal Entry**.
6. The system splits the landed cost across all products in the picking list.
7. Product unit costs are updated accordingly.

### Example: Freight Cost Splitting

| Product | Qty | Weight (kg) | Without Landed Cost | With Landed Cost |
|---|---|---|---|---|
| Product A | 10 | 5 | $10.00/unit | $10.40/unit |
| Product B | 20 | 15 | $5.00/unit | $5.60/unit |

**Freight total:** $150 | **Split method:** By Weight (25 kg total)

- Product A share: (5/25) × $150 = $30 → $3.00/unit added
- Product B share: (15/25) × $150 = $120 → $6.00/unit added

> 💡 **Tip:** Use **By Weight** or **By Volume** for fair cost distribution. Use **Equal** only when all products are similar.

## 11.4 Barcode Scanning

### Dedicated Barcode App

Odoo 18 includes a dedicated **Barcode** application for mobile devices.

1. Install **Barcode** from Apps.
2. Open the Barcode app on a tablet or phone.
3. Connect a Bluetooth barcode scanner or use the device camera.

### Supported Operations in Barcode App

| Operation | What You Can Do |
|---|---|
| **Receipt** | Scan incoming products, confirm quantities, assign lots |
| **Delivery** | Scan picked products, validate shipments |
| **Inventory** | Count stock, update quantities |
| **Transfer** | Move products between locations |
| **Scrap** | Remove damaged stock |

### Barcode Workflow Example (Receiving)

1. Open the Barcode app → **Receipt**.
2. Scan the receipt's barcode (or PO reference).
3. The app shows the first product line.
4. Scan each unit/batch as it comes off the truck.
5. The app counts automatically and shows the running total.
6. When all items are scanned, tap **Validate**.

> 💡 **Tip:** Use the **GS1-128** format for your logistics labels. A single scan can capture product, quantity, lot, and expiry date simultaneously.

## 11.5 Multiple Warehouses

### Setting Up Multi-Warehouse

1. **Inventory → Configuration → Settings**.
2. Enable **Multi-Warehouses**.
3. Create each warehouse under **Inventory → Configuration → Warehouses**.

### Cross-Warehouse Transfers

1. Create a **Route** named e.g., "Replenish from Central DC".
2. Add a **Pull Rule**: Warehouse B pulls from Warehouse A.
3. Create a **Reordering Rule** for each product at Warehouse B.
4. When Warehouse B stock hits the minimum, a transfer from Warehouse A is triggered.

### Warehouse-Specific Product Behavior

Each warehouse tracks its own:
- **On-hand quantity**
- **Forecasted quantity**
- **Reordering rules**
- **Routes**

When viewing a product's quantities, you can filter by warehouse.

> 💡 **Tip:** In reports, add the **Warehouse** dimension to your pivot table to see per-location stock levels.

---

# 12. Common Workflows

## 12.1 Daily Morning Check

1. **Inventory → Operations → Delivery Orders**.
2. Filter: **Confirmed** status.
3. Click **Check Availability** for all deliveries.
4. **Inventory → Reporting → Stock Forecast**.
5. Identify products at risk.
6. Check if any purchase orders are due soon for those products.

## 12.2 Receiving a Supplier Shipment

1. Open **Inventory → Operations → Receipts**.
2. Scan the PO number or find the receipt manually.
3. Compare physical goods against the receipt lines.
4. Enter exact quantities received.
5. Assign lot/serial numbers if tracked.
6. Click **Validate**.
7. If under-received, the backorder is automatically created.
8. **Inventory → Operations → Internal Transfers** (if needed to move from Input to Storage using put-away rules).

## 12.3 Picking and Packing an Order (3-Step)

1. **Inventory → Operations → Pick**.
2. Open the first pick.
3. Click **Check Availability**.
4. Walk the warehouse, scan each item and confirm.
5. Click **Validate**.
6. **Inventory → Operations → Pack**.
7. Open the corresponding pack operation.
8. Scan each item into the package.
9. Print the package label.
10. Click **Validate**.
11. **Inventory → Operations → Delivery Orders**.
12. Find the related delivery.
13. Load the truck, scan packages, validate.

## 12.4 Running a Physical Inventory Count

1. **Inventory → Operations → Inventory Adjustments**.
2. Click **Create → Start Inventory**.
3. Choose scope: **Whole Warehouse**.
4. Print the count sheets (Print → Inventory Report).
5. Count each location. Record quantities on the sheet.
6. Enter counted quantities into Odoo (line by line or with barcode scanner).
7. **Second person verifies** high-value items.
8. Click **Apply All**.
9. Review the valuation journal entry.

## 12.5 Creating a Purchase Order from a Reordering Rule

1. **Inventory → Operations → Reordering Rules**.
2. Identify rules where **Forecast < Min** (highlighted).
3. Click the **Procurement** link to see generated needs.
4. The system may have created a draft PO automatically.
5. **Purchases → Purchase Orders**.
6. Open the draft PO.
7. Review quantities, confirm with supplier.
8. Click **Confirm Order**.

## 12.6 Tracing a Defective Product

1. **Inventory → Reporting → Traceability Report**.
2. Enter the **Lot/Serial Number** of the defective item.
3. View backward trace: Which receipt/supplier did it come from?
4. View forward trace: Which customer deliveries received items from this lot?
5. **Inventory → Operations → Internal Transfers** to quarantine remaining items.
6. **Inventory → Operations → Scrap** if the lot is condemned.

## 12.7 Month-End Closing Checklist

| Step | Action |
|---|---|
| 1 | Run **Inventory Valuation** report and reconcile with GL |
| 2 | Run **Inventory Analysis** — review slow movers/damaged items |
| 3 | Process any pending **Scrap** requests |
| 4 | Validate all pending **Receipts** and **Deliveries** from the month |
| 5 | Run **Cycle Counts** for top-value items |
| 6 | Post all **Landed Costs** for the month |
| 7 | Archive or reconcile **Discrepancy Reports** |
| 8 | Lock the period in **Accounting → Periods** to prevent further changes |

> 💡 **Tip:** Items 1 and 8 are mandatory for clean financials. Schedule them as recurring tasks in Odoo's **Calendar** app.

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Enter` | Validate current document |
| `Alt+T` | Open the **More** menu |
| `Alt+E` | Edit current document |
| `Alt+C` | Create new record |
| `Ctrl+S` | Save |
| `F2` | Rename (in list views) |
| `Ctrl+F` | Search in list |
| `Tab` | After scanning barcode in inventory lines |

## Appendix B: Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| Product not reservable | No stock in selected location | Check product quants; verify location |
| Cannot validate receipt | Missing lot/serial for tracked product | Assign lots before validation |
| Valuation mismatch | Landed costs not posted | Post all landed costs for the month |
| Reordering rule not firing | Rule is inactive or scheduler hasn't run | Activate rule; run scheduler manually |
| Picking shows "Waiting" | Insufficient stock or unconfirmed PO | Check availability; confirm supply orders |
| Duplicate barcode error | Barcode already used by another product | Assign a unique barcode |
| Expired stock not blocked | Expiry monitoring not enabled | Enable Expiration Dates in Settings |

---

*End of Inventory Module User Guide — Odoo 18*
