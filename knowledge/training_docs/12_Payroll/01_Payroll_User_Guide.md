# South Africa Payroll Module — End-User Guide
**Odoo 18** | Training Manual

---

## Table of Contents

1. [Overview: South African Payroll](#1-overview-south-african-payroll)
2. [Setting Up Payroll](#2-setting-up-payroll)
3. [Employee Contracts and Benefits](#3-employee-contracts-and-benefits)
4. [Processing Payslips](#4-processing-payslips)
5. [PAYE, UIF, SDL Calculations](#5-paye-uif-sdl-calculations)
6. [Pension Fund and Medical Aid](#6-pension-fund-and-medical-aid)
7. [Leave and Absence Integration](#7-leave-and-absence-integration)
8. [SARS Reports: EMP201, EMP501, IRP5](#8-sars-reports-emp201-emp501-irp5)
9. [Payslip Printing and Delivery](#9-payslip-printing-and-delivery)
10. [Common Payroll Workflows](#10-common-payroll-workflows)

---

## 1. Overview: South African Payroll

The South Africa Payroll module extends Odoo's native Payroll application with statutory compliance for the South African revenue service (SARS). It handles:

- **PAYE** (Pay-As-You-Earn) — income tax withheld per SARS tax tables.
- **UIF** (Unemployment Insurance Fund) — 1% employee + 1% employer contribution.
- **SDL** (Skills Development Levy) — 1% of gross payroll (employer-only, subject to annual threshold).
- **Pension / Provident fund** contributions (employee and employer).
- **Medical aid** contributions and tax credits.
- **Leave pay** integration with the Odoo Time Off module.
- **SARS reporting**: EMP201 (monthly declaration), EMP501 (bi-annual reconciliation), IRP5/IT3(a) tax certificates.

> **Tip**: This module works hand-in-hand with the **Payroll** and **HR** core apps. Ensure both are installed before proceeding.

---

## 2. Setting Up Payroll

### 2.1 Prerequisites

| App | Technical Name |
|------|----------------|
| Employees | `hr` |
| Payroll | `hr_payroll` |
| South Africa Payroll | `l10n_za_hr_payroll` |
| Time Off | `hr_holidays` (optional, for leave integration) |

### 2.2 Configure Company Settings

1. Go to **Payroll → Configuration → Settings**.
2. Set your **Company** details (registered name, SARS PAYE reference number, UIF reference, SDL reference).
3. Under **South Africa Payroll**:
   - **SARS PAYE Reference Number** — your income tax reference.
   - **UIF Reference Number** — registration number with the Unemployment Insurance Fund.
   - **SDL Reference Number** — Skills Development Levy registration.
   - **SDL Annual Threshold** — gross earnings cap for SDL (check current SARS thresholds; default R1,000,000).
   - **Pension / Provident Fund Rules** — link default fund rules (see Section 6).
4. Click **Save**.

> **Tip**: You can find SARS reference numbers on your **EMP201** return or SARS registration letter.

### 2.3 Salary Rules and Structures

Salary rules define how each line on a payslip is calculated. The module ships with pre-configured rules for South Africa.

#### View Existing Rules
- **Payroll → Configuration → Salary Rules**
- Filter by **Country: South Africa** to see all SA-specific rules.

Key built-in rules:

| Rule | Code | Purpose |
|------|------|---------|
| Basic Salary | `BASIC` | Gross monthly/weekly wage |
| PAYE | `PAYE` | Pay-As-You-Earn tax |
| UIF Employee | `UIF_EE` | 1% of gross ( capped ) |
| UIF Employer | `UIF_ER` | 1% of gross ( capped ) |
| SDL | `SDL` | 1% of gross ( employer, capped ) |
| Pension Fund EE | `PEN_EE` | Employee pension contribution % |
| Pension Fund ER | `PEN_ER` | Employer pension contribution % |
| Medical Aid EE | `MED_EE` | Employee medical aid contribution |
| Medical Aid Tax Credit | `MED_CREDIT` | SARS medical tax credit |
| Leave Pay | `LEAVE_PAY` | Leave payout calculation |

#### Create a Custom Salary Rule

1. Go to **Payroll → Configuration → Salary Rules → Create**.
2. Fill in:
   - **Name** — e.g., "Travel Allowance".
   - **Code** — unique identifier (e.g., `TRAVEL_ALLOW`).
   - **Category** — select or create a category (e.g., `Allowances`).
   - **Country** — South Africa.
   - **Amount Type** — `Fixed Amount` or `Percentage`.
   - **Condition** — Python code that returns `True` when the rule applies (e.g., `contract.travel_allowance > 0`).
   - **Computation** — Python code for the amount.
3. Click **Save**.

#### Salary Structures

Salary structures group rules into a hierarchy. A default **South Africa Monthly** structure is provided.

1. Go to **Payroll → Configuration → Salary Structures**.
2. To create a new structure:
   - **Name** — e.g., "South Africa Weekly".
   - **Country** — South Africa.
   - **Parent** — leave blank for top-level, or select a parent (e.g., `South Africa Monthly`).
   - **Children** — sub-structures (e.g., `Allowances`, `Deductions`).
3. Link **Salary Rules** to the structure via the **Rules** tab.

> **Tip**: Use child structures to group logically: `Earnings`, `Deductions`, `Employer Contributions`, `Leave`.

### 2.4 Payroll Periods

Payroll periods define the frequency and date ranges for payslips.

1. Go to **Payroll → Configuration → Payroll Periods**.
2. Create periods for each month of the tax year (1 March – 28/29 February).
3. Set:
   - **Name** — e.g., "March 2026".
   - **Date From / Date To** — e.g., 1 March 2026 – 31 March 2026.
   - **Schedule Pay** — `Monthly`, `Weekly`, or `Bi-weekly`.
4. Click **Save**.

> **Tip**: Create all 12 months at once using the **Generate Periods** button for speed.

---

## 3. Employee Contracts and Benefits

### 3.1 Create or Edit an Employee Contract

1. Go to **Payroll → Employee Contracts**.
2. Click **Create**.
3. Fill in:
   - **Employee** — select from the employee list.
   - **Job Position** — optional, for reporting.
   - **Wage** — gross monthly (or hourly/weekly) salary.
   - **Schedule Pay** — `Monthly`, `Weekly`, `Bi-weekly`.
   - **Structure** — select the salary structure (e.g., `South Africa Monthly`).
   - **Start Date** / **End Date** — contract validity period.
4. Go to the **South Africa Payroll** tab.

### 3.2 South Africa Payroll Tab Fields

| Field | Description |
|-------|-------------|
| **UIF Number** | Employee's UIF reference (if applicable). |
| **Tax Number** | Employee's income tax number (for IRP5). |
| **Taxable Allowances** | Additional taxable allowances (travel, cell phone, etc.). |
| **Pension Fund** | Link to the employee's pension fund rule. |
| **Pension Fund EE %** | Employee contribution percentage (e.g., 7.5). |
| **Pension Fund ER %** | Employer contribution percentage (e.g., 7.5). |
| **Medical Aid Scheme** | Select the medical aid scheme. |
| **Medical Aid Plan** | Select the specific plan (e.g., "Gold", "Silver"). |
| **Medical Aid Employee Contribution** | Monthly employee contribution amount. |
| **Medical Aid Employer Contribution** | Monthly employer contribution amount. |
| **Medical Aid Dependants** | Number of dependants (used for tax credit). |
| **SDL Exempt** | Check if the employee is exempt from SDL. |
| **UIF Exempt** | Check if the employee is exempt from UIF (e.g., foreign workers). |

### 3.3 Managing Benefits

Pension fund and medical aid schemes are configured globally and then linked per employee.

- **Pension Funds**: Payroll → Configuration → Pension Funds
- **Medical Aid Schemes**: Payroll → Configuration → Medical Aid Schemes
- **Medical Aid Plans**: Payroll → Configuration → Medical Aid Plans

> **Tip**: For new employees, import pension and medical aid elections from the **Onboarding** wizard or HR data load.

---

## 4. Processing Payslips

### 4.1 Generate Payslips (Batch)

1. Go to **Payroll → Payroll Processing → Create Payslips**.
2. Select:
   - **Structure** — `South Africa Monthly` (or Weekly).
   - **Period** — the payroll period (e.g., March 2026).
   - **Employees** — select individuals or choose a department.
3. Click **Generate Payslips**.
4. Odoo creates draft payslips for each employee.

### 4.2 Individual Payslip Generation

1. Go to **Payroll → Payslips → Create**.
2. Select **Employee**, **Contract**, **Structure**, and **Period**.
3. Click **Compute Sheet** to calculate all salary rules.
4. Review each line.

### 4.3 Reviewing and Validating

1. Open a payslip from the list.
2. Click **Compute Sheet** if not yet computed.
3. Review the **Payslip Lines** tab — each line corresponds to a salary rule.
4. Verify:
   - **Gross Pay** -> sum of earnings.
   - **Deductions** -> PAYE, UIF (EE), pension (EE), medical aid.
   - **Employer Contributions** -> UIF (ER), SDL, pension (ER), medical aid (ER).
   - **Net Pay** -> Gross – Deductions.
5. If adjustments are needed:
   - Edit **Payslip Lines** directly, or
   - Add **Input** lines (e.g., one-off bonus, overtime).

> **Tip**: Use the **Payslip Report** (Print → Payslip) to preview before finalising.

### 4.4 Confirm and Post

1. Once verified, click **Confirm** (or **Validate**).
2. The payslip status changes to **Done**.
3. A **Journal Entry** is automatically created in accounting (if the Accounting app is installed).

### 4.5 Batch Confirm

1. Go to **Payroll → Payroll Processing → Process Payroll**.
2. Select the batch of payslips.
3. Click **Process** to confirm all in one go.

### 4.6 Weekly Payroll

1. Create **Weekly** payroll periods.
2. Use the **Weekly** salary structure.
3. Follow the same generation → compute → review → confirm workflow.

> **Tip**: For weekly payroll with overtime, create a custom **Overtime** input rule and ask employees to submit timesheets before processing.

---

## 5. PAYE, UIF, SDL Calculations

### 5.1 PAYE (Income Tax)

PAYE is calculated using the SARS tax tables integrated into the module.

**Formula (simplified)**:
```
Taxable Income = Gross Pay – Pension Fund (EE) – Medical Aid Tax Credit
PAYE = SARS Tax Table lookup on Taxable Income
```

**Tax Tables are updated annually**. To update:
1. Go to **Payroll → Configuration → SARS Tax Tables**.
2. Check the **Effective Date** of the current table.
3. Click **Create** to add a new table for the new tax year (1 March).
4. Enter the rebates, brackets, and thresholds per the latest SARS rates.

> **Tip**: Always load the new tax table **before** processing the first payroll of the new tax year (March).

### 5.2 UIF (Unemployment Insurance Fund)

- **Employee**: 1% of gross pay (capped at the SARS annual threshold / 12 per month).
- **Employer**: 1% of gross pay (same cap).

The module applies the cap automatically based on the **UIF Contribution Cap** setting.

**To check or change the cap:**
1. Payroll → Configuration → Settings.
2. Update **UIF Contribution Cap** to the latest gazetted amount.

### 5.3 SDL (Skills Development Levy)

- **Employer only**: 1% of gross pay.
- **Capped**: the first R1,000,000 (or current threshold) of annual earnings per employee is exempt.

**To update the SDL threshold:**
1. Payroll → Configuration → Settings.
2. Set **SDL Annual Threshold**.

### 5.4 Viewing the Calculation Breakdown

On any confirmed payslip:
- Click **Print → Detailed Report** to see a full breakdown of PAYE, UIF, and SDL computations.
- The **Payslip Lines** tab shows each component with its formula.

---

## 6. Pension Fund and Medical Aid

### 6.1 Pension / Provident Funds

#### Set up a fund
1. Go to **Payroll → Configuration → Pension Funds → Create**.
2. Enter:
   - **Name** — e.g., "ABC Pension Fund".
   - **SARS Registration Number** — fund's SARS reference.
   - **Type** — `Pension` or `Provident`.
   - **Employee Contribution %** — default (overridable per employee).
   - **Employer Contribution %** — default (overridable per employee).
3. Save.

#### Link an employee to the fund
1. Open the employee's **Contract**.
2. In the **South Africa Payroll** tab, select the Pension Fund.
3. Adjust EE% and ER% if different from the fund default.

> **Tip**: Pension contributions reduce taxable income for PAYE purposes. The module handles this automatically.

### 6.2 Medical Aid

#### Set up a scheme
1. Go to **Payroll → Configuration → Medical Aid Schemes → Create**.
2. Name the scheme (e.g., "Discovery Health").
3. Under the **Plans** tab, add plan options (e.g., "Essential", "Comprehensive").

#### Link an employee
1. Open the employee's **Contract**.
2. Select **Medical Aid Scheme** and **Medical Aid Plan**.
3. Enter employee and employer contribution amounts.
4. Enter the number of **Dependants**.

The **Medical Aid Tax Credit** is automatically calculated based on:
- Dependant count (member + 1st dependant = R364/month each; additional = R246/month each — amounts subject to annual SARS updates).

> **Tip**: Update credit amounts in **Payroll → Configuration → Medical Aid Tax Credits** when SARS publishes new values.

---

## 7. Leave and Absence Integration

### 7.1 Prerequisites

- Odoo **Time Off** (`hr_holidays`) must be installed.
- Leave types must be set up with **Payroll Impact** enabled.

### 7.2 Configure Leave Types for Payroll

1. Go to **Time Off → Configuration → Leave Types**.
2. Edit a leave type (e.g., **Annual Leave**, **Sick Leave**).
3. Check **Include in Payroll**.
4. Set **Payroll Impact**:
   - **Deduct from Salary** — unpaid leave will reduce gross pay.
   - **Paid Leave** — payslip includes the leave pay.

### 7.3 Leave Affects Payslips

When you compute a payslip:
- **Unpaid leave days** (e.g., unpaid sick leave) are detected and deducted from gross pay.
- **Paid leave** (annual leave taken) is included as a positive earnings line.
- The payslip line **LEAVE_PAY** reflects the adjustment.

### 7.4 Leave Payout on Termination

When an employee is terminated:
1. Process a **Termination Payslip**.
2. The module includes **Leave Pay** for unused annual leave days.
3. Configure the **Leave Pay Rate** in **Time Off → Configuration → Leave Types** (e.g., 100% of daily wage).

> **Tip**: For unpaid leave, ensure the employee has submitted **Time Off requests** in the system before running payroll — Odoo uses the approved leave days for calculations.

---

## 8. SARS Reports: EMP201, EMP501, IRP5

### 8.1 EMP201 — Monthly SARS Payment Declaration

The EMP201 summarises PAYE, UIF, and SDL due for the month.

1. Go to **Payroll → Reporting → SARS Reports → EMP201**.
2. Select:
   - **Period** — the month.
   - **Company** — if multi-company.
3. Click **Generate EMP201**.
4. Review the report:
   - **Total PAYE** — from all confirmed payslips.
   - **Total UIF** — employee + employer portions.
   - **Total SDL** — employer portion.
   - **Grand Total Due** — sum of all.
5. Click **Print** or **Export to PDF** to file with SARS.

> **Tip**: Cross-check the EMP201 total with the **Payroll Journal** before submitting to SARS.

### 8.2 EMP501 — Bi-Annual Reconciliation

The EMP501 reconciles the two half-years (March–August and September–February).

1. Go to **Payroll → Reporting → SARS Reports → EMP501**.
2. Select the **Half-Year** period.
3. Click **Generate EMP501**.
4. The report includes:
   - Employee tax certificates summary.
   - Monthly EMP201 totals.
   - Difference calculation.
5. Export as CSV or PDF for SARS eFiling upload.

> **Important**: Ensure all payslips for the period are **Confirmed** before generating the EMP501.

### 8.3 IRP5 / IT3(a) Tax Certificates

IRP5 certificates are issued annually to each employee.

1. Go to **Payroll → Reporting → SARS Reports → IRP5 Certificates**.
2. Select the **Tax Year** (e.g., "2026" — March 2026 to Feb 2027).
3. Select **Employees** or leave blank for all.
4. Click **Generate IRP5**.
5. Review each certificate:
   - Employee details and tax number.
   - Gross income, deductions, PAYE paid.
   - Pension and medical aid contributions.
   - UIF and SDL amounts.
6. Click **Print IRP5** for individual copies or **Export CSV** for bulk upload to SARS eFiling.

> **Tip**: Distribute IRP5 certificates to employees before the SARS deadline (usually end of May).

### 8.4 Year-End Procedures

1. Confirm all payslips for the tax year.
2. Generate and review EMP501.
3. Issue IRP5 certificates to employees.
4. Close the payroll year:
   - Go to **Payroll → Configuration → Payroll Periods**.
   - Mark periods as **Closed** to prevent accidental changes.

---

## 9. Payslip Printing and Delivery

### 9.1 Print a Payslip

1. Open the payslip.
2. Click **Print → Payslip**.
3. Choose format:
   - **Standard PDF** — detailed payslip with all lines.
   - **Simplified PDF** — summary view.

### 9.2 Bulk Print

1. Go to **Payroll → Payslips**.
2. Select multiple payslips (checkbox).
3. Click **Print → Payslips (Batch)**.

### 9.3 Email Payslips to Employees

1. Go to **Payroll → Payslips**.
2. Select the payslips to send.
3. Click **Action → Send Payslips by Email**.
4. The email template includes the PDF as an attachment.
5. Click **Send**.

> **Tip**: Customise the email template at **Settings → Technical → Email Templates → Payslip Email**. Add a message like: *"Dear {employee_name}, please find your payslip for {payslip_date} attached."*

### 9.4 Employee Portal

Employees can view their own payslips:
1. Log in to **My Profile → My Payslips**.
2. Download PDF copies for any confirmed payslip.

> **Tip**: Set the portal access rights per employee under **Settings → Users & Companies → Users**.

---

## 10. Common Payroll Workflows

### Workflow A: Monthly Payroll Run

| Step | Action | Menu Path |
|------|--------|-----------|
| 1 | Verify employee contracts are up to date | Payroll → Employee Contracts |
| 2 | Create payroll periods (if not done) | Payroll → Configuration → Payroll Periods |
| 3 | Generate payslips for the period | Payroll → Payroll Processing → Create Payslips |
| 4 | Compute all payslips (batch) | Select batch → **Compute Sheet** |
| 5 | Review each payslip | Open payslip, check lines |
| 6 | Correct any errors (edit lines or inputs) | Payslip → Edit |
| 7 | Confirm payslips | Select batch → **Process** |
| 8 | Generate EMP201 | Payroll → Reporting → SARS Reports → EMP201 |
| 9 | Make SARS payment (outside Odoo) | — |
| 10 | Email payslips to employees | Payslip list → **Send Payslips by Email** |

### Workflow B: New Employee Onboarding

| Step | Action | Menu Path |
|------|--------|-----------|
| 1 | Create employee record | Employees → Create |
| 2 | Create employment contract | Payroll → Employee Contracts → Create |
| 3 | Set up pension/medical aid elections | Contract → South Africa Payroll tab |
| 4 | Capture tax number and UIF number | Contract → South Africa Payroll tab |
| 5 | Process first payslip | Payroll → Payslips → Create (or batch) |

### Workflow C: Employee Termination

| Step | Action | Menu Path |
|------|--------|-----------|
| 1 | Set contract end date | Payroll → Employee Contracts → Edit |
| 2 | Process termination payslip | Payroll → Payslips → Create (final period) |
| 3 | Leave payout is auto-calculated | Check **LEAVE_PAY** line |
| 4 | Confirm payslip | Payslip → **Confirm** |
| 5 | Issue IRP5 certificate | Payroll → Reporting → SARS Reports → IRP5 |

### Workflow D: Correcting a Mistake (Payslip Adjustment)

| Step | Action | Menu Path |
|------|--------|-----------|
| 1 | Reset a confirmed payslip to Draft | Open payslip → **Reset to Draft** |
| 2 | Edit payslip lines or inputs | Payslip → Edit |
| 3 | Re-compute | Click **Compute Sheet** |
| 4 | Re-confirm | Click **Confirm** |
| 5 | If journal entry exists, reverse it | Accounting → Journal Entries → Reverse |

> **Warning**: SARS requires accurate EMP501 reconciliation. Avoid editing past tax-year payslips after year-end closure. Instead, process corrections in the current period.

### Workflow E: Year-End Procedure

| Step | Action | Menu Path |
|------|--------|-----------|
| 1 | Ensure all payslips are confirmed | Payroll → Payslips (filter: Done) |
| 2 | Run EMP501 for H1 (Aug) and H2 (Feb) | Payroll → Reporting → SARS Reports → EMP501 |
| 3 | Generate IRP5 certificates for all employees | Payroll → Reporting → SARS Reports → IRP5 |
| 4 | Distribute IRP5s | Payroll → Reporting → SARS Reports → IRP5 → Print / Email |
| 5 | Close payroll periods | Payroll → Configuration → Payroll Periods → Mark Closed |

---

## Appendices

### A. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Save and close current record |
| `Alt+E` | Edit current record |
| `Alt+C` | Create new record |
| `Alt+D` | Delete current record |
| `Alt+P` | Print menu |

### B. Common Error Messages and Solutions

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| "No salary structure defined" | Contract missing salary structure | Edit contract → select a structure |
| "PAYE rule returned 0" | No valid SARS tax table | Check tax table effective dates |
| "UIF exceeds contribution cap" | UIF cap setting is outdated | Update UIF cap in Settings |
| "Employee not in batch" | Employee has no active contract | Create/update employment contract |
| "Cannot compute: missing input" | Rule requires input data (e.g., overtime) | Add the input on the payslip |

### C. Relevant SARS Resources

- **SARS eFiling**: https://www.sarsefiling.co.za
- **Tax Rates & Thresholds**: SARS website (annual tax tables)
- **UIF Contribution Cap**: Department of Employment and Labour gazette
- **SDL Threshold**: SARS SDL guide

---

*Document version 1.0 — Odoo 18 South Africa Payroll Module*
*Last updated: July 2026*
