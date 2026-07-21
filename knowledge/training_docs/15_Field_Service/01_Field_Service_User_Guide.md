# Odoo 18 Field Service Module — End-User Guide

**Module Maintained by:** OCA (Odoo Community Association)  
**Technical Package:** `fieldservice` (base) + optional addons (`fieldservice_stock`, `fieldservice_portal`, `fieldservice_recurring`, `fieldservice_equipment_stock`, etc.)  
**App Name in Odoo:** Field Service

---

## Table of Contents

1. [Overview](#1-overview)
2. [Initial Configuration and Settings](#2-initial-configuration-and-settings)
3. [Creating Service Orders](#3-creating-service-orders)
4. [Managing Workers and Crews](#4-managing-workers-and-crews)
5. [Route Planning and Scheduling](#5-route-planning-and-scheduling)
6. [Inventory and Equipment Management](#6-inventory-and-equipment-management)
7. [Customer Portal](#7-customer-portal)
8. [Invoicing Field Service Orders](#8-invoicing-field-service-orders)
9. [Reporting and Dashboards](#9-reporting-and-dashboards)
10. [Worksheet Templates](#10-worksheet-templates)
11. [Recurring Orders](#11-recurring-orders)
12. [Tips and Best Practices](#12-tips-and-best-practices)

---

## 1. Overview

The **Field Service module** (OCA `fieldservice`) allows you to manage end-to-end field service operations: from dispatching workers to customer locations, tracking on-site work, managing inventory used in the field, and invoicing for time and materials.

### Key Concepts

| Term | Description |
|------|-------------|
| **Field Service Order (FSM Order)** | A work request that describes a job to be performed at a customer location. |
| **Field Service Location** | The physical address where the work is performed. Can be a customer site, warehouse, or any serviceable location. |
| **Field Service Worker** | A person who performs the field service work. Can be an employee or subcontractor. |
| **Crew** | A group of workers assigned together to complete an order. |
| **Territory / Branch / District / Region** | Hierarchical geographic areas used to organise locations, workers, and orders. |
| **Stage** | The lifecycle step of an order (e.g., New, Scheduled, In Progress, Done, Cancelled). |
| **Order Template** | A reusable template for common types of field service orders (e.g., "AC Installation", "Monthly Maintenance"). |

### Main Menu Structure

```
Field Service
├── Dashboard
│   ├── Orders (Kanban / List / Calendar / Map / Gantt)
│   ├── My Tasks
│   └── Planning (By User / By Project / By Location / By Worksheet Template)
├── Master Data
│   ├── Locations
│   └── Workers
├── Configuration
│   ├── Settings
│   ├── Stages
│   ├── Locations (Branches, Districts, Regions)
│   ├── Workers
│   │   ├── Teams
│   │   └── Categories
│   ├── Order Templates
│   └── Tags
└── Reporting
    ├── By Location
    ├── By Worker
    ├── By Team
    └── By Category
```

---

## 2. Initial Configuration and Settings

Before creating orders, configure the system to match your business process.

### 2.1 Enable the Field Service Module

1. Go to **Apps**.
2. Search for **Field Service**.
3. Click **Install**.

> **Tip:** Install optional addons like `fieldservice_stock`, `fieldservice_portal`, or `fieldservice_recurring` if you need inventory integration, customer portal access, or recurring orders.

### 2.2 Configure Order Stages

Stages represent the lifecycle of an order. Odoo ships with default stages but you can customise them.

1. Go to **Field Service > Configuration > Stages**.
2. Click **Create**.
3. Fill in:
   - **Stage Name** — e.g., "New", "Dispatched", "On Site", "Completed", "Invoiced".
   - **Sequence** — determines the order in which stages appear.
   - **Type** — select **Order**.
   - **Fold in Kanban** — check if this stage should be collapsed in Kanban view (useful for "Cancelled").
   - **Visible in Portal** — (requires `fieldservice_portal`) control whether portal users can see orders in this stage.

> **Tip:** Use clear stage names that match your actual business workflow. Keep the number of stages to 5–7 for simplicity.

### 2.3 Configure Territories, Branches, Districts, and Regions

1. Go to **Field Service > Configuration > Locations**.
2. Create **Branches** (e.g., "Sydney Branch", "Melbourne Branch").
3. Create **Districts** and assign branches to them.
4. Create **Regions** and assign districts.
5. (Optional) Go to **Settings > Users & Companies > Territories** to define territories with ZIP/postal code boundaries.

> **Tip:** Territories can be linked to a default warehouse. In multi-warehouse setups, the `fieldservice_stock` addon will use the territory's warehouse to pull inventory.

### 2.4 Global Settings

Go to **Field Service > Configuration > Settings** and configure:

| Setting | Description |
|---------|-------------|
| **Time and Material Invoicing** | Enables product catalog on orders for billing materials. |
| **Worksheet Templates** | Enables custom digital worksheets to capture data in the field. |
| **Map Routes** | Integrates with MapBox for itinerary planning. |
| **Auto Validate FSM Pickings** | (with `fieldservice_stock`) automatically validates stock moves when an order is completed. |

---

## 3. Creating Service Orders

### 3.1 Manual Order Creation

1. Go to **Field Service > Dashboard > Orders**.
2. Click **Create**.
3. Fill in the required fields:

   | Field | Description |
   |-------|-------------|
   | **Customer** | The contact or company requesting the service. |
   | **Location** | The service address. Select an existing FSM Location or create one on the fly. |
   | **Scheduled Date Start / End** | Planned date/time window for the work. |
   | **Assigned To** | Worker or crew responsible for completing the order. |
   | **Team** | The operations team that owns this order. |
   | **Order Template** | Pre-filled template with tasks, materials, and instructions. |
   | **Tags** | Categorisation tags for filtering and reporting. |
   | **Description** | Detailed work instructions visible to the assigned worker. |

4. Click **Save**.
5. Drag the order through Kanban stages as work progresses (New → Scheduled → In Progress → Done → Invoiced).

> **Tip:** Use the **Activity** button to schedule follow-up calls, reminders, or internal notes on the order.

### 3.2 Creating Orders from a Sales Order

If your process starts with a quotation, you can generate an FSM order automatically.

1. Go to **Sales > Quotations** and create a quotation with a service product.
2. Set the product's **Invoicing Policy** to "Timesheets" or "Delivered Quantity".
3. Under **Service Tracking**, select **Create a task in the Field Service project**.
4. Confirm the sales order. A new FSM order is created automatically.
5. Access the FSM order via the **Tasks** smart button on the sales order.

### 3.3 Creating Orders from a Helpdesk Ticket

1. Open a helpdesk ticket that requires an on-site visit.
2. Click **Create Field Service Order** (visible when Field Service is installed).
3. The ticket details are pre-populated into the new FSM order.

### 3.4 Creating Recurring Orders

If you installed `fieldservice_recurring`:

1. Go to **Field Service > Configuration > Recurring Templates**.
2. Define the recurrence pattern (daily, weekly, monthly, etc.).
3. The system generates new orders automatically based on the schedule.

### 3.5 Order Views

Orders can be viewed in multiple ways:

- **Kanban** — drag-and-drop through stages.
- **List** — tabular view for bulk actions.
- **Calendar** — view orders on a timeline by scheduled date.
- **Map** — (requires MapBox token) view orders on a geographic map.
- **Gantt** — view order durations and overlaps for capacity planning.

> **Tip:** Switch between views using the icons in the top-right of the Orders screen.

---

## 4. Managing Workers and Crews

### 4.1 Creating Workers

1. Go to **Field Service > Master Data > Workers**.
2. Click **Create**.
3. Fill in:
   - **Worker Name** — the person's full name.
   - **Related Partner** — link to an existing contact (employee or subcontractor).
   - **Team** — the field service team this worker belongs to.
   - **Category** — skill or trade category (e.g., "Electrician", "Plumber", "HVAC").
   - **Mobile / Email** — contact details for dispatch communication.
   - **Default Warehouse** — (with `fieldservice_stock`) the van stock or home warehouse for this worker.
   - **Timezone** — important for scheduling across regions.

> **Tip:** Link workers to **Employee** records in the HR module so timesheets and payroll are integrated.

### 4.2 Creating and Managing Teams

1. Go to **Field Service > Configuration > Workers > Teams**.
2. Click **Create**.
3. Set:
   - **Team Name** — e.g., "North Region Crew".
   - **Description** — what this team specialises in.
   - **Sequence** — display order.
4. Assign workers to the team from the worker form.

### 4.3 Worker Categories

1. Go to **Field Service > Configuration > Workers > Categories**.
2. Click **Create**.
3. Set a **Name** (e.g., "HVAC Technician") and optional **Parent Category**.
4. Assign categories to workers to indicate their skills and certifications.

> **Tip:** Use categories to filter available workers when assigning orders. For example, only show electricians for electrical repair orders.

### 4.4 Worker Scheduling

- Assign a single worker to an order via the **Assigned To** field.
- For crew assignments, use the **Crew** field (if the crew addon is installed) or create multiple worker assignments on the order.

---

## 5. Route Planning and Scheduling

### 5.1 Planning Views

Go to **Field Service > Dashboard > Planning** to access:

- **By User** — Gantt chart showing each worker's tasks over time.
- **By Project** — tasks grouped by project, useful for project-based field service.
- **By Location** — tasks grouped by geographic location for route optimisation.
- **By Worksheet Template** — tasks grouped by the type of worksheet used.

> **Tip:** Use the **By Location** planning view to cluster nearby jobs and reduce travel time. Drag and drop to reassign tasks between workers.

### 5.2 Map View and Itineraries

To display orders on a live map with routing directions:

1. **Prerequisite:** Create a MapBox account at https://www.mapbox.com/ and generate an access token.
2. Go to **Settings > General Settings > Integrations**.
3. Paste your MapBox token in the **Map Routes** field.
4. Go to **Field Service > Dashboard > Orders > Map**.
5. Click a pin to see order details, then click **Navigate To** to open directions in Google Maps.

> **Tip:** Remove the "Today" filter to see all upcoming orders on the map. Odoo sorts pins by scheduled date to plot an efficient route.

### 5.3 Calendar View

1. Go to **Field Service > Dashboard > Orders > Calendar**.
2. Switch between day, week, and month views.
3. Drag an order to a new time slot to reschedule.

### 5.4 Gantt View

1. Go to **Field Service > Dashboard > Orders > Gantt**.
2. View all orders on a timeline. Overlapping bars indicate scheduling conflicts.
3. Drag the edges of a bar to adjust duration. Drag the whole bar to reassign to a different date or worker.

> **Tip:** Enable the **Planning** module (if installed) for advanced Gantt-based scheduling with drag-and-drop assignment.

---

## 6. Inventory and Equipment Management

### 6.1 Linking Inventory Locations to FSM Locations

With `fieldservice_stock` installed:

1. Go to **Field Service > Master Data > Locations**.
2. Open or create a location.
3. Set **Inventory Location** to the corresponding stock location in the Inventory app.
4. When parts are consumed on an FSM order, the stock is deducted from this location.

### 6.2 Worker Default Warehouse

Set a default warehouse per worker so materials pulled from inventory are tracked against the right stock location:

1. Go to **Field Service > Master Data > Workers**.
2. Open a worker.
3. In the **Preferences** tab, select a **Default Warehouse** (e.g., "Worker Van Stock").

> **Tip:** If your technicians carry inventory in their vehicles, create a "Van Stock" warehouse per technician and set it as their default. This way stock levels are always accurate in the field.

### 6.3 Consuming Materials on an Order

1. Open an FSM Order.
2. Go to the **Products** or **Materials** tab.
3. Click **Add a line** and select the product, quantity, and warehouse.
4. Confirm the order to trigger a delivery order (picking) that validates the stock move.

> **Tip:** Enable **Auto Validate FSM Pickings** in **Field Service > Configuration > Settings** to automatically complete the stock move when the order stage changes to "Done".

### 6.4 Equipment Management

With `fieldservice_equipment_stock` installed:

1. Go to **Field Service > Master Data > Equipment**.
2. Register equipment installed at customer locations (e.g., serial-numbered assets like AC units, pumps, meters).
3. Link equipment to FSM orders to track maintenance history.
4. View the equipment's service history directly from the equipment form.

---

## 7. Customer Portal

### 7.1 Enabling the Portal

Install the `fieldservice_portal` addon. This allows customers to:

- View field service orders associated with their locations.
- Track order progress.
- Access completed worksheet reports.

### 7.2 Controlling Stage Visibility

1. Go to **Field Service > Configuration > Stages**.
2. Open a stage.
3. Check or uncheck **Visible in Portal**.

> **Tip:** Hide internal stages (e.g., "Draft", "Under Review") from the portal and only show customer-facing stages (e.g., "Scheduled", "In Progress", "Completed").

### 7.3 Customer Experience

1. The customer logs into the Odoo portal at `https://yourcompany.odoo.com/my`.
2. Under **Field Service**, they see a list of orders associated with their company's locations.
3. Each order shows the stage, scheduled date, assigned worker, and description.
4. Completed orders include downloadable worksheet reports and invoices.

---

## 8. Invoicing Field Service Orders

### 8.1 Enabling Time and Material Invoicing

1. Go to **Field Service > Configuration > Settings**.
2. Enable **Time and Material Invoicing**.

### 8.2 Invoicing from a Sales Order (Recommended)

The standard workflow is to create a sales order first, then generate FSM tasks from it.

1. **Create a Sales Order** in the Sales app for the customer.
   - Add service products with **Invoicing Policy** set to "Timesheets" or "Delivered Quantity".
   - Set **Service Tracking** to "Create a task in the Field Service project".
2. **Confirm the Sales Order**. An FSM order is created automatically.
3. **Complete the FSM Order** — the worker records time and materials on the order.
4. **Return to the Sales Order** — click the **Tasks** smart button, then **Sales Order** to go back.
5. Click **Create Invoice** → select **Regular Invoice** → click **Create Draft Invoice**.
6. Review the invoice lines (they include time entries and material costs) and **Confirm**.

> **Tip:** Always link FSM orders to sales orders for clean, auditable billing. Avoid standalone FSM orders if invoicing is required.

### 8.3 Invoicing Directly from an FSM Order

If the order is not linked to a sales order:

1. Open the FSM order.
2. Click **Create Invoice** at the top of the form.
3. A draft invoice is generated with any recorded products and timesheet lines.
4. Review and confirm the invoice in the Invoicing app.

### 8.4 Invoicing from the Mobile App

Technicians can create invoices directly from the field:

1. In the Odoo mobile app, open the assigned FSM order.
2. Click **Create Invoice**.
3. Choose invoice type: **Regular Invoice** or **Down Payment**.
4. The invoice is created in draft status and can be sent to the customer immediately.

> **Tip:** Use the mobile app to capture customer signatures and send the invoice while still on site — this accelerates payment cycles.

### 8.5 Timesheet-Based Invoicing

1. Workers log time on the FSM order using the **Timesheets** tab.
2. If the order is linked to a sales order with a service product invoiced "Based on Timesheets", the time entries are automatically billable.
3. Generate the invoice as described in 8.2.

---

## 9. Reporting and Dashboards

### 9.1 Dashboard Overview

The **Field Service Dashboard** provides a high-level view of all orders:

- Counts by stage (New, Scheduled, In Progress, Done).
- Orders requiring attention (overdue, unassigned).
- Quick links to create new orders.

### 9.2 Reporting Menu

Go to **Field Service > Reporting** to access:

- **By Location** — analysis of orders, time spent, and costs per service location.
- **By Worker** — performance metrics per worker (orders completed, average duration, travel time).
- **By Team** — team-level KPIs.
- **By Category** — breakdown by work category (e.g., HVAC vs. Electrical).

### 9.3 Pivot and Graph Views

All reporting views support pivot tables and graphical charts:

- Click the **Pivot** icon to create a cross-tabulation of order data.
- Click the **Graph** icon to switch between bar, line, and pie chart representations.
- Use filters and group-by options to drill down (e.g., by date range, territory, stage).

> **Tip:** Save frequently used report configurations as **Favorites** (star icon) for quick access.

### 9.4 Custom Measures

You can report on any field in the system. Common measures include:

- Number of orders per worker.
- Average time to complete an order.
- Total materials cost per location.
- Revenue per territory.

---

## 10. Worksheet Templates

### 10.1 Creating a Worksheet Template

1. Go to **Field Service > Configuration > Worksheet Templates**.
2. Click **Create**.
3. Design the form using Odoo's QWeb layout:
   - Add sections for data entry (text fields, checkboxes, dropdowns, signatures).
   - Include placeholders for dynamic data (e.g., customer name, order reference).
4. Save the template.

### 10.2 Assigning Worksheets to Orders

- On the **Order Template** form, select a **Worksheet Template**.
- On an individual **FSM Order**, you can also override the worksheet.
- When the worker opens the order on mobile, the worksheet appears as a fillable form.

### 10.3 Completing and Signing Worksheets

1. The worker fills out the worksheet on-site (e.g., checklist items, measurements, photos).
2. Capture the customer's digital signature directly on the worksheet.
3. Click **Send Report** to email a PDF copy to the customer.
4. The completed worksheet is stored on the order and available in the portal.

> **Tip:** Use worksheets for regulatory compliance (e.g., safety checklists) or service verification (e.g., "customer approved the work").

---

## 11. Recurring Orders

### 11.1 Setting Up Recurring Templates

Requires `fieldservice_recurring` addon.

1. Go to **Field Service > Configuration > Recurring Templates**.
2. Click **Create**.
3. Define:
   - **Name** — e.g., "Monthly HVAC Filter Change".
   - **Interval** — every X days/weeks/months.
   - **Next Date** — when the first recurring order should be generated.
   - **Order Template** — the FSM order template to use.
4. The system creates new orders on the defined schedule.

### 11.2 Managing Recurring Instances

- Each generated order is independent and can be rescheduled, reassigned, or cancelled.
- The recurring template tracks a history of all orders it has created.
- To pause or stop recurrence, deactivate the template.

> **Tip:** Use recurring orders for maintenance contracts, periodic inspections, or scheduled cleaning services.

---

## 12. Tips and Best Practices

| # | Tip |
|---|-----|
| 1 | **Always link FSM orders to Sales Orders** when billing is required. This ensures all time and materials are captured on the invoice. |
| 2 | **Use categories for worker skills** — this helps dispatchers assign the right person to the right job. |
| 3 | **Leverage the Map view** — it reduces travel time and fuel costs by grouping nearby jobs. |
| 4 | **Set a default warehouse per worker** — especially for van stock, so inventory is always accurate. |
| 5 | **Use order templates** for repetitive work — they save data entry and ensure consistency. |
| 6 | **Train workers on the mobile app** — worksheets, timesheets, signatures, and invoicing can all be done from the field. |
| 7 | **Review stages periodically** — remove unused stages and rename them if your process changes. |
| 8 | **Schedule orders in the Gantt view** — overlapping bars highlight conflicts before dispatch. |
| 9 | **Enable portal visibility per stage** — only show stages that are meaningful to customers. |
| 10 | **Use tags** for advanced filtering — e.g., "Urgent", "Warranty", "New Customer". |

---

*End of Guide — Field Service Module (OCA) for Odoo 18*

*For module source code and issue tracking, visit https://github.com/OCA/field-service*
