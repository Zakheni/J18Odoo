# Odoo 18 — HR & Employees Module
## End-User Training Manual

---

# Table of Contents

1. [Overview](#1-overview)
2. [Creating and Managing Employee Records](#2-creating-and-managing-employee-records)
3. [Departments & Job Positions](#3-departments--job-positions)
4. [Contracts Management](#4-contracts-management)
5. [Time Off / Leave Management](#5-time-off--leave-management)
6. [Attendance Tracking (Check-In / Check-Out)](#6-attendance-tracking)
7. [Expense Management](#7-expense-management)
8. [Reporting: Employee Directory & Org Chart](#8-reporting)

---

## 1. Overview

The **HR & Employees** module is the central hub for managing your organisation's workforce in Odoo 18. It stores every employee record, links to departments and job positions, and integrates tightly with Contracts, Time Off, Attendance, Expenses, Recruitment, and Payroll.

**Key capabilities:**
- Employee master data (personal info, work info, HR info)
- Department and job position hierarchies
- Employment contracts with history
- Leave requests and allocation
- Check-in / check-out attendance
- Expense reporting
- Organisational charts and directory reports

> **Tip:** The HR module works best when all employees have a linked **User** (login). This enables self-service for leaves, expenses, and attendance.

---

## 2. Creating and Managing Employee Records

### 2.1 Add a New Employee

1. Navigate to **Employees → Employees**.
2. Click **Create**.
3. Fill in the required fields:
   - **Name** — Full name of the employee
   - **Department** — Select from existing departments
   - **Job Position** — Select from existing positions
4. Optionally fill:
   - **Work Email** / **Work Phone**
   - **Manager** — The employee's direct supervisor
   - **Coach** — Mentor (can differ from manager)
   - **Company** — Leave blank for the main company
5. Click **Save**.

### 2.2 Personal & HR Information Tabs

After saving, several tabs become available:

| Tab | Fields | Purpose |
|-----|--------|---------|
| **Personal Information** | Birthday, Gender, Nationality, ID Number, Marital Status, Children | Demographic data |
| **HR Settings** | Employee Type (Employee/Student/Trainee/etc.), Visa info, Bank Account | Payroll and compliance |
| **Work Information** | Location, Working Hours, Timezone | Operational planning |
| **Private Information** | Personal Email, Personal Phone, Emergency Contact | Emergency / GDPR |

> **Tip:** Use the **Employee Type** field to distinguish regular employees from interns, subcontractors, or volunteers. This affects leave eligibility and contract defaults.

### 2.3 Employee Status

Each employee has a **Status** field that controls what HR actions are available:

- **Draft** — Not yet active
- **Active** — Current employee; can log attendance, request leaves, submit expenses
- **Inactive** — Former employee; historical data is preserved

To archive an employee: click the **Archive** button on the form view.

### 2.4 Employee Badges & Tags

Use **Tags** (a many-to-many field on the employee form) for custom groupings such as:
- "Remote Worker"
- "First Aid Trained"
- "Company Car"

Tags are configured under **Employees → Configuration → Employee Tags**.

---

## 3. Departments & Job Positions

### 3.1 Managing Departments

1. Navigate to **Employees → Configuration → Departments**.
2. Click **Create**.
3. Enter:
   - **Department Name**
   - **Parent Department** — For hierarchical tree structure
   - **Manager** — The department head
4. Click **Save**.

The department tree is visible in **Employees → Reporting → Org Chart**.

### 3.2 Managing Job Positions

1. Navigate to **Employees → Configuration → Job Positions**.
2. Click **Create**.
3. Enter:
   - **Job Title**
   - **Department**
   - **Target Number of Employees** (optional — used in Recruitment)
4. Click **Save**.

> **Tip:** Job Positions are shared with the **Recruitment** module. A position marked "New Recruitment" will appear as a vacancy on the website.

### 3.3 Hierarchy Example

```
Company
└── Sales Department
    ├── Sales Manager
    │   ├── Senior Sales Rep
    │   └── Junior Sales Rep
    └── Sales Support
└── Engineering Department
    ├── Engineering Manager
    ├── Backend Developer
    └── Frontend Developer
```

---

## 4. Contracts Management

### 4.1 Overview

The **Contracts** submodule stores employment contracts and manages salary information, working hours, and leave allocations.

**Prerequisite:** Enable the Contracts feature under **Employees → Configuration → Settings → Contracts**.

### 4.2 Create a Contract

1. Open the employee record.
2. Go to the **Contracts** tab.
3. Click **Add a line**.
4. Fill in:
   - **Start Date** — Contract commencement
   - **End Date** — Leave blank for open-ended contracts
   - **Wage** — Gross salary (period depends on configured payroll)
   - **Schedule Pay** — Monthly, bi-weekly, hourly, etc.
   - **Working Schedule** — Linked to a Working Hours template
   - **HR Responsible** — Person managing this employee
5. Click **Save**.

> **Tip:** For multi-company setups, each contract can be linked to a different company.

### 4.3 Contract States

| State | Meaning |
|-------|---------|
| **Draft** | Not yet valid; editable |
| **Running** | Currently active |
| **Expired** | Passed the end date |
| **Cancelled** | Manually cancelled |

Only one contract per employee can be **Running** at any time.

### 4.4 Linking Contracts to Payroll (Optional)

When the **Payroll** app is installed, contracts become the source of:
- Basic salary (Wage)
- Struct, allowances, deductions
- Leave accrual rules

---

## 5. Time Off / Leave Management

### 5.1 Overview

The **Time Off** module handles leave types, allocations, requests, and approvals. It integrates with Contracts to determine accrual rules.

### 5.2 Leave Types

1. Navigate to **Time Off → Configuration → Leave Types**.
2. Click **Create**.
3. Configure:
   - **Name** — e.g., "Annual Leave", "Sick Leave"
   - **Color** — For calendar visualisation
   - **Allocation Type**:
     - *No Allocation* — Unlimited; no need to pre-allocate
     - *Allow Negative* — Can go into negative balance
     - *Fixed* — Fixed number of days per period
     - *Based on Working Schedule* — Calculated proportionally
   - **Validation** — One or two levels of approval
   - **Employee Eligibility** — Which employee types can use this leave type

> **Tip:** Create a "Work From Home" leave type with **No Validation** to allow self-service logging without approval.

### 5.3 Allocate Leave to Employees

1. Navigate to **Time Off → Allocations → Allocations**.
2. Click **Create**.
3. Fill in:
   - **Employee** (or *All Employees* for bulk)
   - **Leave Type**
   - **Number of Days**
4. Click **Save → Confirm**.

You can automate this via **Time Off → Configuration → Leave Types → [Type] → Accrual Rules**.

### 5.4 Request Time Off (Employee Self-Service)

1. Navigate to **Time Off → Time Off** (or click **My Time Off** from the Dashboard).
2. Click **Create**.
3. Select:
   - **Leave Type**
   - **Date From / Date To** (or half-day, or specific hours)
   - **Reason** (optional)
4. Click **Save → Submit**.

### 5.5 Approve / Refuse Time Off (Manager)

1. Navigate to **Time Off → Time Off**.
2. Switch to **List or Calendar view**.
3. Click a pending request.
4. Choose:
   - **Approve** — Leave is granted
   - **Refuse** — Enter a reason; employee is notified
5. Alternatively, use **My Approvals → Time Off** from the Dashboard.

### 5.6 Leave Calendar

The **Time Off → Calendar** view shows all approved leaves across the organisation. Use the filter at the top to view by department or team.

> **Tip:** Enable **Show on Dashboard** for leave types to display remaining balances on each employee's dashboard.

---

## 6. Attendance Tracking

### 6.1 Overview

The **Attendance** module records when employees check in and check out. It can be used in two modes:
- **Kiosk mode** (shared terminal at reception)
- **User-based mode** (each employee checks in via their own account)

### 6.2 Enable Attendance

1. Navigate to **Employees → Configuration → Settings**.
2. Under **Attendance**, check:
   - **Attendances** — Enable check-in / check-out
3. Configure optional settings:
   - **Pin Code** — Require a pin for kiosk mode
   - **Attendances with Barcode** — Scan badges

### 6.3 Check In / Check Out (Employee)

**Via the Dashboard:**
- Click **Check In** (green button) or **Check Out** (red button).
- The timestamp and current location (IP-based) are recorded.

**Via the App:**
- Use My Profile → Attendance → Check In / Check Out.

**Via Kiosk:**
- Open the **Attendance Kiosk** app on a shared tablet/computer.
- Employee selects their name (or scans barcode), enters PIN if required, and clicks **Check In / Out**.

### 6.4 View Attendance Records

1. Navigate to **Attendances → Attendances**.
2. View in:
   - **List view** — Raw check-in/check-out timestamps
   - **Pivot view** — Aggregate worked hours by week/month/employee
   - **Graph view** — Visual analysis

### 6.5 Manual Corrections

Managers can adjust attendance:
1. Open the attendance record (or create a new one).
2. Modify the **Check In** / **Check Out** time.
3. Add a **Reason** for the adjustment.
4. Save.

> **Tip:** Use **Attendances → My Attendances** for a personal view with a real-time status indicator (Checked In / Checked Out).

---

## 7. Expense Management

### 7.1 Overview

Employees submit expense claims (travel, supplies, mileage) that are approved by managers and optionally invoiced or reimbursed via Payroll.

### 7.2 Submit an Expense (Employee)

1. Navigate to **Expenses → My Expenses**.
2. Click **Create**.
3. Fill in:
   - **Description** — What was purchased
   - **Employee** — Auto-filled to yourself
   - **Category** — e.g., Travel, Meals, Accommodation
   - **Total Amount**
   - **Date**
   - **Attach Receipt** — Drag and drop an image/PDF
4. Optionally:
   - **Bill Reference** — Supplier invoice number
   - **Analytic Account** — For project costing
   - **To Reimburse** — Amount to give back to employee
5. Click **Save → Submit**.

While in **Draft**, you can edit or delete. Once **Submitted**, it goes to the approval chain.

### 7.3 Approve Expenses (Manager)

1. Navigate to **Expenses → Expenses to Approve**.
2. Review the receipt and details.
3. Click **Approve** or **Refuse**.
4. *Refused* expenses require a reason and return to Draft so the employee can correct them.

### 7.4 Post / Reimburse Expenses (HR/Accounting)

1. From **Expenses → Expenses to Post**.
2. Click **Post Journal Entries** — Creates accounting moves.
3. For reimbursement via payroll, use **Expenses → Expenses → Action → Register Payment** or create a **Salary Rule** in Payroll.

> **Tip:** Enable **"Multi-Level Approval"** in **Expenses → Configuration → Settings** for expenses above a threshold.

---

## 8. Reporting

### 8.1 Employee Directory

1. Navigate to **Employees → Reporting → Employee Directory**.
2. View all employees in a searchable list with filters:
   - Department
   - Job Position
   - Location
   - Company
3. Click any employee row to open their form view.
4. Use the **Print** button at the top to export as PDF.

**Export options:**
- Click the gear icon → **Export All** → Choose fields → Export to XLSX or CSV.

### 8.2 Organisational Chart

1. Navigate to **Employees → Reporting → Org Chart**.
2. The org chart displays in a graphical tree view.
3. **Interactive controls:**
   - Drag to pan
   - Scroll to zoom
   - Click a node to view employee details
   - Click the **Expand/Collapse** arrows to show or hide subordinates
4. Use the **Options** dropdown:
   - **Show Manager** — Highlight reporting lines
   - **Show Only Direct Subordinates** — Flatten the view
   - **Include Inactive Employees** — Greyed-out nodes for former employees

> **Tip:** The org chart respects the **Manager** field on each employee record and the **Parent Department** hierarchy for departmental grouping.

### 8.3 Employee Analysis (Pivot & Graph)

Available under **Employees → Reporting → Employee Analysis**.

- **Pivot view** — Count employees by department, job, contract type, etc.
- **Graph view** — Visual distribution (bar, line, pie).
- **Measures** — Employee Count, Average Wage, Contract Length, etc.

### 8.4 Attendance Reports

1. Navigate to **Attendances → Reporting → Attendance Report**.
2. Shows hours worked per employee per day/week/month.
3. Use filters:
   - **Date Range**
   - **Department**
   - **Employee**
4. Export to Excel for payroll processing.

### 8.5 Time Off Reports

1. Navigate to **Time Off → Reporting → Leave Analysis**.
2. Shows leave taken by type, department, and month.
3. Use **Pivot** or **Graph** views for trend analysis.
4. Export for headcount planning and compliance.

### 8.6 Expense Reports

1. Navigate to **Expenses → Reporting → Expense Analysis**.
2. Analyse spending by:
   - Employee / Department
   - Expense Category
   - Time Period
3. Use **Pivot view** for a matrix breakdown (e.g., Total by Department and Category).

---

## Appendix: Common Troubleshooting

| Issue | Solution |
|-------|----------|
| Employee cannot see Time Off menu | Ensure they have the **Time Off** group: Settings → Users → [User] → App Access |
| Check-in button is missing | Enable attendance in Employees → Settings |
| Leave balance shows 0 | Verify leave allocation exists and is confirmed; check contract is **Running** |
| Cannot approve subordinate's leave | Make sure the manager is set in the employee's **Manager** field, and the employee is listed as a **Subordinate** of the manager |
| Org chart is empty | Verify employees have a **Manager** assigned |
| Expense receipt won't upload | File must be under 32 MB; supported formats: PNG, JPG, PDF |

---

*This guide applies to Odoo 18 Community and Enterprise editions. Some features (Payroll integration, multi-level approvals) require the Enterprise edition or corresponding company add-ons.*
