# Odoo 18 Projects — End-User Manual

---

## Table of Contents

1. [Overview](#1-overview)
2. [Creating Projects and Tasks](#2-creating-projects-and-tasks)
3. [Task Stages and the Kanban View](#3-task-stages-and-the-kanban-view)
4. [Assigning Tasks and Managing Deadlines](#4-assigning-tasks-and-managing-deadlines)
5. [Timesheets and Tracking Hours](#5-timesheets-and-tracking-hours)
6. [Project Profitability and Margins](#6-project-profitability-and-margins)
7. [Gantt Chart and Planning](#7-gantt-chart-and-planning)
8. [Reporting and Dashboards](#8-reporting-and-dashboards)

---

## 1. Overview

The **Odoo 18 Projects** module helps teams plan, execute, and monitor projects of any size. It integrates tightly with **Timesheets**, **Sales**, **Inventory**, and **Accounting** to give you a single source of truth for project delivery and financial performance.

### Key Capabilities

- **Task management** — Create, organise, and track tasks across multiple stages.
- **Kanban, List, Form, Calendar, Gantt, and Pivot views** — Choose the right view for your workflow.
- **Timesheets** — Log hours directly on tasks; automatically compute costs.
- **Profitability analysis** — See planned vs. actual costs and revenue at a glance.
- **Gantt planning** — Schedule tasks on a timeline with dependencies.
- **Multi-level reporting** — Dashboards, pivot tables, and graphical charts.
- **Portal access** — Let customers or external collaborators see their projects.

> **Tip:** The Projects module works out of the box, but its real power appears when you connect it to Sales Orders (for invoicing) and Accounting (for cost recognition).

---

## 2. Creating Projects and Tasks

### 2.1 Create a New Project

1. Go to **Projects → Projects**.
2. Click **Create**.
3. Fill in the key fields:

   | Field | Description |
   |-------|-------------|
   | **Project Name** | A descriptive title (e.g. *Website Redesign — Acme Corp*). |
   | **Customer** | (Optional) Link a customer from Contacts. |
   | **Privacy** | `Private` (only team members) or `Portal` (visible to customer via portal). |
   | **Allow Timesheets** | If checked, team members can log hours. |
   | **Allow Recurring Tasks** | Enable for tasks that repeat on a schedule. |

4. (Optional) Set a **Project Manager** and assign **Team Members** on the **Settings** tab.
5. Click **Save**.

### 2.2 Create a Task

1. Open a project.
2. Click the **Tasks** smart button or go to **Projects → Tasks** and select the project.
3. Click **Create**.
4. Enter at least a **Title**. Recommended fields:

   | Field | Purpose |
   |-------|---------|
   | **Title** | Short, action-oriented name (e.g., *Design homepage mockup*). |
   | **Description** | Detailed instructions, acceptance criteria, or checklists. |
   | **Deadline** | Expected completion date. |
   | **Assigned To** | Team member responsible. |
   | **Tags** | Colour-coded labels for filtering (e.g., `bug`, `urgent`). |
   | **Stage** | Current workflow stage (see Section 3). |
   | **Customer** | Automatically inherited from the project if set. |

5. Click **Save**.

> **Tip:** Use the **Description** field to include a Markdown checklist. Odoo renders it with checkable boxes.

### 2.3 Sub-tasks

You can nest tasks under a parent task:

1. Open a task.
2. Go to the **Sub-tasks** tab.
3. Click **Add a line** → create or link an existing task.

Sub-tasks inherit the parent's project and customer. Progress is rolled up to the parent.

---

## 3. Task Stages and the Kanban View

### 3.1 Default Stages

Every project comes with a default stage set: **To Do → In Progress → Done**. You can fully customise them.

### 3.2 Customise Stages

1. Go to **Projects → Configuration → Stages**.
2. Click **Create**.
3. Provide a **Stage Name** (e.g., *Code Review*, *QA Testing*).
4. (Optional) Set a **Sequence** number to control ordering.
5. Check **Fold** if you want this stage to collapse into a single line in Kanban (useful for *Done* / *Cancelled*).

> **Tip:** Stages are shared across all projects unless you limit them via the **Project** field on the stage form.

### 3.3 Using the Kanban View

The Kanban view is the default view for tasks. It shows columns for each stage and cards for tasks.

- **Move a task** — Drag and drop a card from one column to another.
- **Quick edit** — Click the **pencil icon** on a card to edit the title, deadline, or assignee inline.
- **Colour coding** — Kanban cards can show a colour based on **Tags**, **Priority**, or **Stage** (configured under **Project Settings → Kanban Colour**).
- **Right-click (or three-dot menu)** — Access actions like *Log timesheet*, *Add subtask*, or *Delete*.

> **Tip:** Kanban columns respect stage folding. When a stage is folded, tasks inside it are hidden to keep the interface clean.

---

## 4. Assigning Tasks and Managing Deadlines

### 4.1 Assign a Task

1. Open a task or create a new one.
2. In the **Assigned To** field, select a user from the dropdown.
3. (Optional) Add multiple assignees using the **Assignees** tab (Odoo 18 supports multi-assignment).

The assignee receives:
- An **in-app notification** (bell icon).
- An **email** if email notifications are enabled under **Project Settings → Messages and Tasks**.

### 4.2 Set a Deadline

1. In the task form, click the **Deadline** field.
2. Select a date from the date-picker.
3. Tasks with deadlines appear in the **Calendar** view and on the assignee's **dashboard**.

### 4.3 Deadline Alerts

- **Overdue tasks** are highlighted in red in list and Kanban views.
- Project managers can see all upcoming deadlines on the **Project Overview** dashboard.

> **Tip:** Enable **Recurring Tasks** in the project settings to auto-create tasks on a schedule (e.g., *Weekly report due every Friday*).

---

## 5. Timesheets and Tracking Hours

### 5.1 Log Hours on a Task

1. Open a task.
2. Click the **Timesheets** smart button (or **Timesheets** tab).
3. Click **Add a line**.
4. Fill in:

   | Field | Description |
   |-------|-------------|
   | **Date** | Defaults to today. |
   | **Description** | What you worked on. |
   | **Duration** | Time spent (format `1:30` or `1.5`). |

5. Click **Save**.

**Alternative (quick entry):**

1. Go to **Timesheets → My Timesheets**.
2. Click **Create** or use the **Timesheet Grid** view.
3. Select the **Project** and **Task**.
4. Enter the hours and description.

> **Tip:** Use the **Timesheet Timer** on the task form — click the **play icon** to start/stop tracking. Time is automatically logged when you stop.

### 5.2 Approve Timesheets

1. Go to **Timesheets → Approve Timesheets**.
2. Review lines. Select the ones to approve.
3. Click **Approve** (or **Validate** if the workflow requires it).

### 5.3 Timesheet Grid View

For weekly bulk entry:

1. Go to **Timesheets → My Timesheets**.
2. Switch to the **Grid** view.
3. Enter hours in the day‑column cells. Odoo auto‑highlights weekends and public holidays.

> **Tip:** The grid view respects the company's working calendar. Hours exceeding the daily limit appear in orange.

---

## 6. Project Profitability and Margins

### 6.1 Access Profitability

1. Open a project.
2. Click the **Profitability** smart button.

The page is split into four sections:

| Section | What it shows |
|---------|---------------|
| **Revenue** | Invoiced amount + amounts to invoice (linked from Sales Orders). |
| **Cost** | Employee timesheet cost + non‑employee expenses linked to the project. |
| **Profit** | Revenue minus Cost. |
| **Margin** | Profit / Revenue (percentage). |

### 6.2 Understanding the Numbers

- **Planned vs. Actual** — The **Rates** column compares budgeted (from the Sales Order) versus actual hours and costs.
- **Drill-down** — Click any number to see the underlying timesheet lines, expenses, or invoices.

### 6.3 Set a Budget

1. Go to **Projects → Configuration → Analytic Accounts**.
2. Open the analytic account linked to your project.
3. On the **Budgets** tab, set the planned amounts.

Odoo will then show budget vs. actual variance in the profitability report.

> **Tip:** Profitability requires at least one **Sales Order Item** linked to the project. If you do not use Sales, you can manually enter revenue lines under the **Revenue** tab of the project form.

---

## 7. Gantt Chart and Planning

### 7.1 Switch to Gantt View

1. Open a project (or go to **Projects → Tasks** and filter by project).
2. Click the **Gantt** icon in the view switcher (top‑right).

Tasks appear as horizontal bars on a timeline. Drag the edges to resize, or drag the entire bar to shift the start date.

### 7.2 Dependencies

1. In the Gantt view, hover over a task bar.
2. Click and drag the **dependency handle** (small circle at the left or right edge) to another task bar.
3. A dependency arrow appears.

Dependencies are stored on the task's **Dependencies** tab and can also be managed there.

> **Tip:** Use the **Filters** in the Gantt view to show only tasks assigned to a specific person or tasks in a certain stage.

### 7.3 Scheduling Options

- **Auto‑schedule** — Odoo can automatically shift tasks when a dependency is moved (enable in Gantt view **Options**).
- **Milestones** — Create a task with no duration (start = end date) to mark a milestone.

---

## 8. Reporting and Dashboards

### 8.1 Project Dashboard

1. Go to **Projects → Dashboard**.
2. The dashboard shows:
   - **Number of projects** and **tasks** (total, done, overdue).
   - **My Tasks** — tasks assigned to you, grouped by stage.
   - **Timesheet summary** — hours logged this week / month.

Click any card to drill into the underlying list.

### 8.2 Pivot View

1. Go to **Projects → Tasks**.
2. Switch to **Pivot** view.
3. Drag dimensions (e.g., *Project*, *Stage*, *Assignee*) into rows or columns.
4. Drag measures (e.g., *Count*, *Hours Planned*, *Hours Spent*) into the value area.

This is useful for **capacity planning** and **bottleneck analysis**.

### 8.3 Graphical Reports

1. Go to **Projects → Reporting → Project Analysis**.
2. Use the **Measure** dropdown to switch between *Number of Tasks*, *Hours Planned*, *Hours Spent*, etc.
3. Change the chart type (Bar, Line, Pie) as needed.

> **Tip:** Save your favourite filter/grouping combinations as **Favourites** (star icon) for one‑click access.

### 8.4 Custom Dashboards (Studio)

If you have the **Odoo Studio** module:

1. Go to **Dashboard** (main Apps menu).
2. Click **Create**.
3. Add **Project‑related datasets** (e.g., *Tasks by Stage*, *Timesheet by Project*).
4. Arrange tiles and charts to create an executive overview.

---

## Appendix — Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `c` | Create a new task (in list/kanban) |
| `Ctrl + Enter` | Save current form |
| `Ctrl + K` | Search / Command palette |
| `Esc` | Close form / discard draft |
| `←` / `→` | Previous / Next task (in form view) |

---

*Document version 1.0 — Odoo 18 Community Edition. For questions or corrections, contact your system administrator.*
