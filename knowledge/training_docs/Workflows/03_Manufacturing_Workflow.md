# 03 — Manufacturing Workflow (MTO / MTS)
**Module**: Sales → Manufacturing → Inventory → Accounting
**Version**: Odoo 18

---

## Overview

The Manufacturing workflow integrates Sales, Manufacturing (MRP), Inventory, and Accounting. It covers Make-to-Order (MTO) and Make-to-Stock (MTS) scenarios — from a Sales Order triggering production, through Bill of Materials explosion, component consumption, finished goods receipt, delivery, and cost analysis.

```
Sales Order ──→ Manufacturing Order ──→ Component Pick ──→ Produce ──→ Finished Product Receipt ──→ Delivery ──→ Cost Analysis
```

### Swimlane — Role Responsibility Matrix

| Step | Sales Rep | Production Planner | Manufacturing User | Inventory User | Accountant |
|------|-----------|-------------------|--------------------|----------------|------------|
| 1. SO → MO | Create SO | Confirm MO | — | — | — |
| 2. BOM & Availability | — | Check component stock & trigger reordering | — | — | — |
| 3. MO Processing | — | — | Start production, record components & finished qty | — | — |
| 4. Finished Product Receipt | — | — | Validate finished product receipt | Validate if needed | — |
| 5. Delivery to Customer | — | — | — | Process delivery | — |
| 6. Cost Analysis | — | Review | — | — | Validate costing entries |

---

## Step 1 — Sales Order → Manufacturing Order (MTO)

### Who
**Sales Rep** creates and confirms the Sales Order.
**Production Planner** reviews and confirms the Manufacturing Order.

### Procedure

1. **Sales Order Creation** (standard process, see Workflow 01):
   - Sales → Quotations → Create
   - Add a product of type **"Stockable"** with **Route = Manufacture (MTO)**
   - Confirm the Sales Order
   - ![Screenshot Description: Sales Order line — product row shows "Route: Manufacture" in the Route column, indicating MTO routing. The order lines show a Manufacture badge next to the product name.]

2. **Auto-Generated Manufacturing Order**:
   - Upon SO confirmation, Odoo automatically creates:
     - **Manufacturing Order** (Manufacturing → Operations → Manufacturing Orders)
     - **Component Pick** (Inventory → Operations → Pickings)
   - ![Screenshot Description: Manufacturing Order list — a new draft MO linked to the SO is visible. Columns: Reference, Product, Quantity To Produce, Scheduled Date, Status (Draft/Confirmed/In Progress/Done).]

3. **Review the MO**:
   - Open the MO from Manufacturing → Operations → Manufacturing Orders
   - Key fields:
     - **Product**: Finished product to manufacture
     - **Quantity**: Matches the SO quantity (or higher if configured)
     - **Bill of Material**: Auto-selected based on BOM rules (variant, quantity ranges, etc.)
     - **Routing**: Work center, operation steps, and duration
     - **Consume Materials**: Tab listing all components and required quantities
     - **Scheduled Production Date**: Based on SO commitment date minus manufacturing lead time
   - ![Screenshot Description: MO form — header shows Product, Quantity, BOM, Routing. "Consume Materials" tab lists components with "To Consume" and "Consumed" qty columns. Smart-buttons: "Check Availability", "Plan", "Start", "Done".]

4. **Confirm the MO**:
   - Click **"Confirm"** button
   - Status changes: *Draft* → *Confirmed*
   - The component picking is now visible and waiting

---

## Step 2 — BOM & Component Availability Check

### Who
**Production Planner** checks and ensures component availability.

### Procedure

1. **Bill of Materials Review**:
   - Manufacturing → Products → Bills of Materials → select the BOM
   - Structure display:
     ```
     ╔══════════════════════════════════════╗
     ║  Finished Product  (Qty: 1 Unit)     ║
     ║  ┌─ Component A (Qty: 2)            ║
     ║  │   ┌─ Sub-component A1 (Qty: 3)   ║  ← Phantom BOM (nested)
     ║  ├─ Component B (Qty: 1)            ║
     ║  ├─ Component C (Qty: 5)            ║
     ║  └─ Operation: Assembly (30 min)    ║
     ╚══════════════════════════════════════╝
     ```
   - ![Screenshot Description: BOM form — top shows "Bill of Material" with product, quantity, routing. "Components" tab shows a list of raw materials with quantities. "Operations" tab shows work centers, duration, and cost per operation.]

2. **Check Availability**:
   - On the MO form, click **"Check Availability"**
   - Odoo checks on-hand stock for each component
   - Result displayed per component:
     - ✅ **Available** — sufficient stock at the source location
     - ❌ **Waiting** — insufficient stock; component needs procurement
     - ⚠️ **Partially Available** — some stock exists but not enough

3. **Handle Shortages**:
   | Situation | Recommended Action |
   |-----------|-------------------|
   | Component out of stock | Create PO or internal transfer to replenish |
   | Component is manufactured (sub-assembly) | Auto-generates a sub-MO (if BOM is phantom or sub-assembly type) |
   | Component lead time too long | Re-schedule the MO with Production Planner override |
   | Alternative component | Edit the BOM for this production lot (one-off substitution) |

4. **Reordering (if needed)**:
   - Odoo auto-procures components with *Buy* route: Purchase Orders auto-created
   - Sub-assemblies with *Manufacture* route: Sub-MOs auto-created
   - ![Screenshot Description: Reordering view — a side panel or wizard shows "Products to Order" with supplier, quantity, lead time. Tabs for "Suggested POs" and "Suggested MOs".]

5. **Plan the MO**:
   - Once all components are available, click **"Plan"** (visible on confirmed MO)
   - Status: *Confirmed* → *Planned*
   - The MO is now on the production schedule (Gantt chart view available)

---

## Step 3 — Manufacturing Order Processing

### Who
**Manufacturing User** executes production on the shop floor.

### Procedure

1. **Start Production**:
   - Open the MO → Click **"Start"**
   - Status changes: *Planned* → *In Progress*
   - Timestamp recorded for labor tracking
   - ![Screenshot Description: MO in "In Progress" state — timer visible showing elapsed time. The "Start" button is now replaced by "Done" and "Record Components". A work-order panel shows each operation with start/stop buttons.]

2. **Work Order Execution** (if routing/work centers configured):
   - Manufacturing → Operations → Work Orders
   - Each operation shown with:
     - Work center assignment
     - Standard duration (from the routing)
     - Start / Pause / Stop buttons
   - Operator can clock in at the tablet terminal
   - ![Screenshot Description: Work Order tablet or form view — shows operation name, work center, elapsed time, buttons for "Start", "Pause", "Problems". Below: raw materials consumed at this step. A barcode scanner input field at the bottom.]

3. **Record Component Consumption**:
   - Click **"Record Components"** (or "Consume Materials" on the MO)
   - Options:
     - **Automatic**: Components auto-consumed when MO is set to Done
     - **Manual**: Scan or enter lot/serial for each component
   - Lot tracking: If products are lot-tracked, scan each lot at consumption
   - ![Screenshot Description: "Consume Materials" dialog — table with Component, Qty To Consume, Qty Already Consumed, Lot/Serial scan field. A "Consume" button confirms each line.]

4. **Handle Production Issues**:

   | Issue | Resolution |
   |-------|------------|
   | Component damaged during production | Record as scrap: click "Scrap" button → select component & quantity |
   | Component shortage on floor | Force consumption with a backorder; replenish separately |
   | Defective finished product | Record quantity as "Defective" in the MO; create rework order |
   | Production exceeds MO qty | Overproduction handled by qty tolerance (configured on BOM) |

5. **Set to Done**:
   - Click **"Produce"** (or **"Done"**)
   - Wizard: Enter **Finished Quantity** produced (defaults to MO qty)
   - If quantity < planned: backorder created automatically
   - If quantity > planned: overproduction recorded (if within tolerance)
   - Click **"Validate"**
   - ![Screenshot Description: "Produce" wizard — input field "Quantity", dropdown for "Finished Product Lot/Serial" (if tracked), checkboxes for "Consume All Components" and "Create Backorder".]

---

## Step 4 — Finished Product Receipt to Stock

### Who
**Manufacturing User** completes this step automatically when the MO is set to Done.
**Inventory User** may validate if double-validation is enabled.

### Procedure

1. **Automatic Receipt**:
   - When MO is set to *Done*, Odoo automatically:
     - Increases on-hand quantity of the finished product
     - Reduces on-hand quantity of all consumed components
     - Creates a **Stock Move** record (Manufacturing → Input → Stock)
     - Generates a **Stock Valuation Layer** (if perpetual valuation is active)
   - ![Screenshot Description: Stock Move from MO — source location "Production" to destination "Stock". Product, quantity, and reference values shown. Status is "Done".]

2. **Validate Finished Product** (if double-validation):
   - Inventory → Operations → Manufacturing → select the receipt
   - Click **"Validate"** to confirm
   - Lot/Serial assignment: scan or enter the lot number for the finished batch

3. **Traceability**:
   - Serial/Lot numbers of components are linked to the finished product lot
   - Navigate: Manufacturing → Tracing → Serial/Lot Traceability
   - ![Screenshot Description: Lot traceability tree — top: finished product lot #LOT-001; branches: consumed component lots A-100, B-200, C-300; origin: Sales Order SO-042; destination: Delivery Order D-015.]

---

## Step 5 — Delivery to Customer

### Who
**Inventory User** handles the outgoing delivery.

### Procedure

1. **Delivery Order** (created when SO was confirmed in Step 1):
   - Inventory → Operations → Delivery Orders
   - The delivery is linked to the original SO
   - Status changes automatically:
     - *Waiting* → *Available* (when MO is completed and stock is available)
   - ![Screenshot Description: Delivery Order list — a delivery with status "Available". Reference, Scheduled Date, Partner, Origin (SO number).]

2. **Process the Delivery**:
   - Open the delivery → **"Validate"**
   - Confirm the finished product quantity matches the SO quantity
   - Assign lot/serial number from the finished batch (must match the lot produced)
   - Click **"Validate"**
   - Status: *Available* → *Done*

3. **Invoice the Customer**:
   - Return to the Sales Order → **"Create Invoice"**
   - Standard invoicing procedure (see Workflow 01, Steps 4-5)

---

## Step 6 — Cost Analysis

### Who
**Accountant** reviews and validates the manufacturing costs.
**Production Planner** monitors cost variances for continuous improvement.

### Procedure

1. **Access Cost Analysis**:
   - Manufacturing → Reporting → Manufacturing Analysis
   - ![Screenshot Description: Manufacturing Analysis pivot table — rows: Products/MO reference; columns: Cost categories. Pivot displays Material Cost, Labor Cost, Overhead Cost, Total Cost, and Unit Cost.]

2. **Cost Breakdown**:

   | Cost Component | Source | Calculation |
   |----------------|--------|-------------|
   | **Raw Material Cost** | Component product cost (Standard / FIFO / Average) | Sum of (component qty × unit cost) for all consumed components |
   | **Labor Cost** | Work center cost per hour | Operation duration × work center hourly cost |
   | **Overhead Cost** | Work center overhead + BOM-level overhead % | Fixed overhead per operation + percentage of material cost |
   | **Total Cost** | Sum of above | = Material + Labor + Overhead |
   | **Unit Cost** | Total ÷ Finished Quantity | Cost per unit of finished product |

3. **Review Inventory Valuation**:
   - Accounting → Reporting → Inventory Valuation → filter by product
   - Shows standard cost vs actual cost per unit
   - ![Screenshot Description: Inventory Valuation report — Product, Quantity, Unit Cost (Standard), Unit Cost (Actual), Valuation Difference. Variances highlighted in red/amber.]

4. **Analyze Variances**:

   | Variance Type | Description | Who Investigates |
   |---------------|-------------|------------------|
   | **Material Price Variance** | Actual component price ≠ standard cost | Accountant |
   | **Material Usage Variance** | Actual qty consumed ≠ BOM standard qty | Production Planner |
   | **Labor Efficiency Variance** | Actual labor hours ≠ standard hours | Production Planner |
   | **Volume Variance** | Produced qty ≠ planned qty | Planner + Sales |

5. **Period-End Cost Revaluation** (if using Standard Cost):
   - Accounting → Accounting → Ad-Hoc → Revaluation
   - Revalues all inventory to new standard costs
   - Post the revaluation journal entry

6. **MO Cost Report** (per order):
   - Open the MO → **"Cost Analysis"** smart-button
   - Detailed cost report:
     ```
     ╔══════════════════════════════════════════════╗
     ║  MO-00042 — Assembly: Finished Product X    ║
     ║══════════════════════════════════════════════║
     ║  Cost Category      | Planned   | Actual    ║
     ║  ───────────────────┼───────────┼────────── ║
     ║  Raw Material        | $120.00   | $125.50  ║
     ║  Labor               | $ 45.00   | $ 52.30  ║
     ║  Overhead            | $ 20.00   | $ 20.00  ║
     ║  ───────────────────┼───────────┼────────── ║
     ║  Total               | $185.00   | $197.80  ║
     ║  Unit Cost           | $ 37.00   | $ 39.56  ║
     ║  Variance            |           | +$12.80  ║
     ╚══════════════════════════════════════════════╝
     ```

---

## Complete End-to-End Flow Diagram (Text)

```
 SALES                MANUFACTURING                    INVENTORY              ACCOUNTING
 ┌──────┐          ┌──────────────────┐             ┌─────────────┐          ┌──────────────┐
 │  SO   │──Auto──→│  Manufacturing   │             │ Component    │          │  Draft Invoice│
 │(Confirmed)│      │  Order (Draft)   │             │ Picking      │          │  (from SO)    │
 └──────┘          └────────┬─────────┘             │ (Draft)     │          └──────┬───────┘
       │                     │                       └──────┬──────┘                 │
       │                     ▼ Confirm                       ▼                        │
       │              ┌──────────────────┐             ┌─────────────┐                │
       │              │  MO (Confirmed)  │───────→      │  Component  │                │
       │              └────────┬─────────┘ Check Avail  │  Ready      │                │
       │                       │                        └─────────────┘                │
       │                       ▼ Start                                                  │
       │              ┌──────────────────┐                                              │
       │              │  MO (In Progress)│                                              │
       │              │  ─ Consume comp  │──→ Stock moves: Component │                  │
       │              │  ─ Produce       │     OUT (-)              │                  │
       │              └────────┬─────────┘     Finished (+)         │                  │
       │                       │                                    │                  │
       │                       ▼ Done                               │                  │
       │              ┌──────────────────┐        ┌─────────────┐    │                  │
       │              │  MO (Done)       │─────→   │  Finished    │    │                  │
       │              │  + Finished Qty  │         │  Product     │    │                  │
       │              └──────────────────┘         │  In Stock    │    │                  │
       │                                            └──────┬──────┘    │                  │
       │                                                   │            │                  │
       │                                                   ▼ Delivery   ▼ Validate Invoice
       │                                            ┌─────────────┐  ┌──────────────┐
       │                                            │  Delivered  │──│  Posted      │
       │                                            │  to Customer│  │  Invoice     │
       └────────────────────────────────────────────┴─────────────┘  └──────────────┘
                                                                            
                                COST ANALYSIS ──────────────┬──────────────┘
                                                             │
                                                      ┌──────────────┐
                                                      │  Variance    │
                                                      │  Report      │
                                                      └──────────────┘
```

---

## Key Configuration Points

| Setting | Path | Impact |
|---------|------|--------|
| Route: Manufacture | Manufacturing → Configuration → Settings → Manufacturing → Routes | Enables MTO product flow |
| Bill of Materials | Manufacturing → Products → Bills of Materials | Defines components, operations |
| Routing | Manufacturing → Configuration → Routing → Work Centers | Work center costs, operation durations |
| Work Center Cost | Manufacturing → Configuration → Work Centers → Cost tab | Hourly labor & overhead cost |
| Component Consumption | Manufacturing → Configuration → Settings → "Consume materials automatically" | Auto vs manual consumption |
| Overproduction Tolerance | Manufacturing → BOM → Options tab | % allowed over MO qty |
| Backorders | Manufacturing → Configuration → Settings → "Create backorder if produced qty < planned" | Auto-backorder for underproduction |
| Inventory Valuation | Accounting → Configuration → Settings → Inventory Valuation | Standard / FIFO / Average |
| Traceability | Manufacturing → Configuration → Settings → "Traceability by Lot/Serial" | Full lot chain tracking |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| MO not auto-created from SO | Product route ≠ Manufacture | Assign "Manufacture" route to product |
| Components not consuming | Consumption mode = Manual | Record components before setting Done |
| MO stuck on "Waiting" | Insufficient component stock | Check availability, create PO for shortage |
| Wrong BOM selected | BOM rules (variant, qty range) not configured | Adjust BOM sequence or rules |
| Cost not showing in analysis | No cost set on components / operations | Update product cost or work center hourly rate |
| Variance too large | Standard cost outdated | Run period-end revaluation |
| Lot traceability broken | Lots not scanned at consumption | Use barcode scanning for all consumptions |
| Finished product can't be delivered | Wrong lot assigned in receipt | Trace and correct lot assignment |

---

*End of Workflow 03 — Manufacturing*
