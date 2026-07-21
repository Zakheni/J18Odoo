# Odoo 18 Manufacturing Module — End-User Guide

> **Document version:** 1.0  
> **Applies to:** Odoo 18 Enterprise & Community  
> **Objective:** Provide step-by-step instructions for day-to-day manufacturing operations.

---

## Table of Contents

1. [Overview of Manufacturing in Odoo](#1-overview-of-manufacturing-in-odoo)
2. [Bill of Materials (BOMs)](#2-bill-of-materials-boms)
3. [Manufacturing Orders](#3-manufacturing-orders)
4. [Work Orders & Routing](#4-work-orders--routing)
5. [Subcontracting](#5-subcontracting)
6. [Quality Control](#6-quality-control)
7. [Reporting (Cost Analysis, Inventory)](#7-reporting-cost-analysis-inventory)
8. [MRP Multi-Level Planning](#8-mrp-multi-level-planning)
9. [Appendix: Keyboard Shortcuts & Tips](#9-appendix-keyboard-shortcuts--tips)

---

## 1. Overview of Manufacturing in Odoo

The Manufacturing module transforms raw materials into finished products. It integrates tightly with Inventory, Sales, Purchasing, and Quality.

**Key concepts:**

| Term | Meaning |
|------|---------|
| **Bill of Materials (BOM)** | Recipe that lists components and operations needed to make a product. |
| **Manufacturing Order (MO)** | A production order that consumes materials and produces finished goods. |
| **Work Order** | A single step within a manufacturing order (requires *Routing*). |
| **Routing** | Defines the sequence of work centres and operations. |
| **Subcontracting** | Outsourcing part or all of production to an external partner. |

> **Tip:** Enable *"Multi-Step Routes"* in Inventory settings to use advanced push/pull flows for manufacturing.

### Navigation

- Go to **Manufacturing → Dashboard** to see a kanban view of MOs by state.
- Use the **main menu** to access Masters (BOMs, Routings), Operations (MOs, Work Orders), and Reporting.

---

## 2. Bill of Materials (BOMs)

A BOM defines how a product is made: which components, in what quantity, and which operations.

### 2.1 Create a Bill of Materials

1. Go to **Manufacturing → Bill of Materials → Create**.
2. **Product**: Select the finished product. The *Product Type* must be *Storable Product*.
3. **Quantity**: Enter the number of units this BOM produces (e.g., `1.00`).
4. **BOM Type**:
   - *Manufacture this product* — you produce it.
   - *Kit* — the product is a kit of components (no manufacturing order).
   - *Subcontracting* — a subcontractor produces it.
5. **Routing**: Optionally select a routing (see [Section 4](#4-work-orders--routing)).
6. **Components tab** — Add raw materials:

   | Field | Description |
   |-------|-------------|
   | Product | The raw material / sub-assembly. |
   | Quantity | Amount needed per BOM quantity. |
   | Unit of Measure | Must match the product's UoM. |

7. **By-Products tab** — Add any by-products produced (e.g., scrap that has value).
8. **Operations tab** — If no routing is selected, list operations manually.
9. **Miscellaneous** — Set *Lead Time* (days), *Properties*, *Notes*.
10. Click **Save**, then **Validate BOM** to confirm.

> **Tip:** Use the **"BoM Structure"** report under Reporting to visualise the component tree.

### 2.2 Versioning a BOM

- You can create a new **Version** from an existing BOM. Go to the BOM form → *Versions* smart button.
- Each version can be *Active* or *Obsolete*.
- The active version is used when confirming Manufacturing Orders or running MRP.

### 2.3 BOM Configuration Options

- **Consumption**: *Strict* (exact qty), *Flexible* (allow variance), or *Based on BoM*.
- **Allow Alternative Products**: Let operators substitute materials on the shop floor.
- **Sequence**: Priority when multiple BOMs exist for the same product.

> **Tip:** Use *Flexible* consumption when actual material usage varies (e.g., chemicals, paints).

---

## 3. Manufacturing Orders

A Manufacturing Order (MO) consumes materials to produce finished goods.

### 3.1 Create a Manufacturing Order

1. **From a Sales Order**: Confirm the SO → *Delivery* tab → click **Create Manufacturing Order**.
2. **From the Manufacturing app**:  
   a. Go to **Manufacturing → Operations → Manufacturing Orders → Create**.  
   b. **Product**: Select the product to manufacture.  
   c. **Quantity**: Enter the quantity to produce.  
   d. **BOM**: Auto-filled if one exists.  
   e. **Routing**: Auto-filled from the BOM.  
   f. **Source Location** and **Destination Location** (default: *Stock → Production → Stock*).
   g. **Deadline Start** and **Deadline End**.
3. Click **Confirm Order**.

### 3.2 Planning

- **Plan manually**: After confirmation, the MO is in *Confirmed* state.
- **Plan automatically**: Install the *MRP* module (for multi-level planning) or set up *Reordering Rules*.
- Use the **"Generate Work Orders"** button to create work orders if a routing is attached.

### 3.3 Reserve & Check Availability

- Click **Check Availability** to reserve raw materials.
- **Components availability** is shown in the *Components* tab via a colored dot:
  - 🟢 Green = Reserved
  - 🟡 Yellow = Partially available
  - 🔴 Red = Not available

### 3.4 Produce

1. Click **Start Production** to log the operator and begin.
2. **Record Production**:
   - The **Produce** wizard opens.
   - *Lot/Serial Number* — optionally assign to finished product.
   - *Consume materials* — check / uncheck lines to over- or under-consume.
   - *By-Products* — record any produced by-products.
3. Click **Validate** to finish.

> **Tip:** Use **"Mark as Todo"** to create a work order queue for operators.

### 3.5 Post-Production

- The MO moves to *Done* state.
- Inventory is updated: components are deducted, finished goods are added.
- **Cost is computed**: Actual cost = sum of component costs + operations costs.

### 3.6 Unfinished / Scrap

- **Scrap during production**: Use **Scrap** button on the MO to scrap defective components.
- **Cancel an MO**: Use the *Cancel* button (only when not yet started).
- **Unlink an MO**: In *Draft* state, delete it.

### 3.7 MO States Summary

| State | Meaning |
|-------|---------|
| Draft | Not yet confirmed. |
| Confirmed | Confirmed; materials not yet reserved. |
| Planned | Work orders generated. |
| In Progress | Production started. |
| Done | Finished. |
| Cancelled | Cancelled. |

---

## 4. Work Orders & Routing

Routings define the *sequence of operations* and their *work centres*.

### 4.1 Create a Routing

1. Go to **Manufacturing → Master Data → Routings → Create**.
2. **Name**: e.g., *Assembly Line A*.
3. **Operations** tab — Add each step:

   | Field | Description |
   |-------|-------------|
   | Sequence | Order of the operation. |
   | Work Centre | Where it is performed. |
   | Duration | Time in minutes (or hours via UoM). |
   | Standard Time | Expected cycle time per unit. |
   | Description | Instructions for the operator. |

4. **Work Centres** (Manufacturing → Master Data → Work Centres):
   - Set *Capacity* (number of units per cycle), *Efficiency*, *Time per Unit*.
   - Define *Working Hours* and *Costs per hour*.

5. Link the routing to a BOM (see [2.1 Create a BOM](#21-create-a-bill-of-materials)).

> **Tip:** Use **"Time Efficiency"** on work centres to account for learning curves.

### 4.2 Work Order Lifecycle

1. An MO creates work orders automatically when a routing is present.
2. Operators see work orders in **Manufacturing → Work Orders**.
3. Actions:
   - **Start**: Log start time.
   - **Pause**: Pause the operation.
   - **Block**: Flag an issue (requires unblock).
   - **Done**: Confirm the operation is complete.

4. Work order dependencies: Next operation cannot start until the previous one finishes (unless *chaining* is disabled).

### 4.3 Work Order Tablets

- Odoo 18 provides a responsive **Tablet View** for operators.
- Access via the tablet icon or direct URL: `/manufacturing/work_orders/tablet`.
- Operators can scan barcodes, record start/stop, report issues, and scrap.

> **Tip:** Enable **"Barcode Scanner"** in Inventory settings for rapid scanning on the shop floor.

---

## 5. Subcontracting

Subcontracting lets you send materials to a partner who performs manufacturing on your behalf.

### 5.1 Setup

1. **Enable Subcontracting**:  
   Go to **Inventory → Configuration → Settings** → tick *Subcontracting*.

2. **Configure the Subcontractor Contact**:  
   In the partner form, tick **Is a Subcontractor**. Set the *Subcontracting Location* (default: *Partner Location*).

3. **Create a BOM for Subcontracting**:  
   a. Create a new BOM.  
   b. Set **BOM Type** = *Subcontracting*.  
   c. The **Subcontractor** field appears — select the partner.  
   d. Add components as usual.

### 5.2 Create a Subcontracting MO

1. Go to **Manufacturing → Operations → Manufacturing Orders → Create**.
2. Select the product and BOM (type = *Subcontracting*).
3. Confirm the MO.
4. A **Purchase Order** (with service line) is automatically created for the subcontractor.
5. **Send materials**: The *Resupply Route* automatically creates a delivery order to the subcontractor.
6. When subcontractor finishes, validate the incoming shipment on the purchase order.
7. The MO is completed automatically.

> **Tip:** Use **"Subcontracting Reporting"** under Reporting to track subcontractor performance.

### 5.3 Subcontracting with Components Provided

- The subcontractor's *Consumption* can be *Strict* or *Flexible*.
- Use **"Track Components"** to require the subcontractor to report consumption in the *IoT Box* or portal.

---

## 6. Quality Control

Odoo 18's Quality module integrates with Manufacturing and Work Orders.

### 6.1 Quality Points

A *Quality Point* defines when, where, and how a quality check is triggered.

1. Go to **Quality → Quality Control → Quality Points → Create**.
2. **Trigger**: *On Receipt*, *On Delivery*, *On Start of Production*, *On Operation*, *On Completion*.
3. **Product** / **Product Category**: Optional filter.
4. **Operation**: Select the work order operation.
5. **Control per Lot**: Tick to check every lot.
6. **Type**: *Instructions*, *Take a Picture*, *Register a Measure*, etc.
7. **Team**: Optionally assign to a quality team.

### 6.2 Quality Checks

- Checks appear automatically based on triggers.
- Go to **Quality → Quality Control → Quality Checks**.
- Actions:
  - **Pass** / **Fail**.
  - **Measure**: Record a numerical measurement with tolerances.
  - **Picture**: Attach image evidence.
  - **Instructions**: Display work instructions to operator.

### 6.3 Alert / Blocking

- A failed check can **Block** the production order or work order.
- A supervisor must **Unblock** from the work order or quality check form.

> **Tip:** Configure **"Quality Alert"** email templates to notify managers on failure.

---

## 7. Reporting (Cost Analysis & Inventory)

### 7.1 Manufacturing Reports

Access from **Manufacturing → Reporting**:

| Report | Description |
|--------|-------------|
| **Manufacturing Orders Analysis** | Pivot / graph view of MOs by state, product, user, date. |
| **BOM Structure** | Multi-level tree of components for a BOM. |
| **Work Order Analysis** | Hours worked, efficiency, cost per work centre. |
| **Inventory Forecast** | Stock + incoming - outgoing projected over time. |

### 7.2 Cost Analysis

- **Standard Cost vs Actual Cost**:  
  - Standard cost is set on the product form.  
  - Actual cost is computed when the MO is done.  
- View cost variance via **Manufacturing Orders Analysis** → add *Cost* measures.
- **Valuation**: Go to *Inventory → Reporting → Inventory Valuation*.

> **Tip:** Run **"MRP Cost Structure"** report to see cost breakdown per BOM level.

### 7.3 Inventory Reports

- **Inventory Dashboard**: *Inventory → Reporting → Inventory Dashboard*.
- **Stock Moves History**: Traceability of every stock move tied to MOs.
- **Traceability Report**: Serial / Lot genealogy (Inventory → Reporting → Traceability).

---

## 8. MRP Multi-Level Planning

The *MRP (Material Requirements Planning)* sub-module automates procurement and production for multi-level BOMs.

### 8.1 Enable MRP

- Install **MRP** module from Apps.
- Go to **Manufacturing → MRP → MRP** to open the dashboard.

### 8.2 Run MRP

1. Click **Run MRP** in the top-left.
2. A wizard opens:
   - **Start Date** / **End Date**: Planning horizon.
   - **Demand**: Choose *All Open Orders*, *Specific Products*, or *By Schedule*.
3. Click **Run**.

### 8.3 MRP Results

MRP creates:

- **Manufacturing Orders** for sub-assemblies and finished products.
- **Purchase Orders** for raw materials not produced in-house.
- **Suggestions** are grouped by product, with a *To-Order Quantity*.

### 8.4 Reordering Rules

MRP relies on *Reordering Rules* (Inventory → Configuration → Reordering Rules).

| Field | Meaning |
|-------|---------|
| Product | The item to procure. |
| Location | The warehouse / location. |
| Minimum Quantity | Trigger level for reorder. |
| Maximum Quantity | Target stock after reorder. |
| Multiple Quantity | Order in multiples of this qty. |
| Lead Time | Days to receive / produce. |

- Set **Order Point** = Minimum Qty.
- Set **Order Quantity** = Maximum – Minimum (or fixed, or *Economic Order Quantity*).
- Run **"Order Once"** to immediately generate draft orders from rules.

> **Tip:** Use **"Days to Order"** found in Inventory dashboard for safety lead time.

### 8.5 Exploded vs Current BOM

- **Current BOM** — only direct components.
- **Exploded BOM** — all levels unrolled (used by MRP to plan sub-assemblies).

Toggle in the MO form: *BOM* → *Exploded* checkbox.

---

## 9. Appendix: Keyboard Shortcuts & Tips

### General Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + S` | Save record. |
| `Ctrl + Enter` | Save & close. |
| `Ctrl + K` | Search / command palette. |
| `Ctrl + Shift + K` | Search more. |
| `Alt + ←` / `Alt + →` | Navigate back / forward. |
| `Ctrl + P` | Print current record. |

### Manufacturing Tips

- **Duplicate a BOM**: Click the *Action* cog → *Duplicate*.
- **Inventory by MO**: Click the stock icon next to each component to view stock count.
- **Locked MOs**: A completed MO cannot be edited unless set as *Locked* → *Unlock*.
- **Demand by Product**: In MRP, click a product line to see the demand source (SO, MO, forecast).
- **Report an issue mid-production**: Click *Issues* on the work order tablet → create a quality alert.

---

*End of document. Last updated: July 2026.*
