# Quality Control — User Guide

**Module:** quality_control_oca (OCA)  
**Applies to:** Odoo 18  
**Role:** Quality User / Quality Manager  

---

## 1. Overview

The Quality Control module (OCA `quality_control_oca`) enables you to define **inspection points**, trigger **quality checks** on products, pickings, or manufacturing orders, and manage **non-conformities** when a check fails. It replaces the standard Odoo 18 Quality module with a more flexible, OCA-driven workflow.

---

## 2. Prerequisites

- Access rights: *Quality / User* or *Quality / Manager*.
- Products must exist and be stockable (or consumable) if used in picking checks.
- Picking types (Warehouse → Configuration → Picking Types) should be configured if you plan to inspect incoming/outgoing shipments.
- Manufacturing orders (MO) must be in a confirmed or in-progress state to run in-process checks.

---

## 3. Key Concepts

| Term | Definition |
|---|---|
| **Inspection Point** | A rule that defines *when* and *on what* a quality check must be performed (e.g. "on receipt of Product A"). |
| **Quality Check** | The actual test or measurement recorded against an inspection point. |
| **Non-Conformity** | A problem report created when a check returns a failed result. |
| **Control per Product** | Inspection points tied to a specific product. |
| **Control per Picking** | Inspection points triggered by a transfer (receipt, delivery, internal). |

---

## 4. Step-by-Step Instructions

### 4.1 Create an Inspection Point

1. Go to **Quality → Configuration → Inspection Points**.
2. Click **New**.
3. Fill in the fields:

   | Field | Value / Description |
   |---|---|
   | **Name** | e.g. *Inspect raw material X on receipt* |
   | **Company** | Leave default unless multi-company |
   | **Active** | Keep checked |
   | **Control Type** | Choose **Product** or **Picking** |
   | **Product** | If Control Type = Product, select the product |
   | **Picking Type** | If Control Type = Picking, choose the operation (Receipts, Delivery, etc.) |
   | **Trigger** | *On Confirmation* / *On Transfer* / *Manual* |
   | **Team** | (Optional) Quality team responsible |
   | **Test Type** | *Pass / Fail*, *Quantitative*, or *Qualitative* |

4. Click **Save**.

### 4.2 Perform a Quality Check

Checks can be generated automatically (based on your inspection points) or manually.

**Automatic generation:**

- When a picking is validated or a product is received, the system creates a pending quality check.
- Go to **Quality → Quality Checks** to see all open checks.

**Manual check:**

1. Go to **Quality → Quality Checks** and click **New**.
2. Select the **Inspection Point** (or leave blank for ad-hoc).
3. Fill the **Product**, **Lot/Serial** (if tracked), and **Picking**.
4. Enter the **Test Result**:
   - *P/F* → Toggle the result.
   - *Quantitative* → Enter a measured value and tolerance limits.
   - *Qualitative* → Select from predefined options.
5. Click **Confirm** to record the result.

### 4.3 Handle a Failed Check (Non-Conformity)

1. From a failed quality check, click **Create Non-Conformity**.
2. A new non-conformity record opens with the check data pre-filled.
3. Set the **Severity**:
   - *Minor*
   - *Major*
   - *Critical*
4. Describe the **Problem** and **Root Cause** (if known).
5. Assign a **Responsible** person.
6. Define a **Corrective Action** in the *Actions* tab.
7. Click **Confirm Non-Conformity**.

### 4.4 Review Non-Conformities

1. Go to **Quality → Non-Conformities**.
2. Filter by status: *Draft*, *Confirmed*, *In Progress*, *Done*.
3. Open a record to update the resolution, attach photos, or close the NC.

---

## 5. Common Tasks

| Task | Steps |
|---|---|
| **Define quality checks per product** | Inspection Point → Control Type = Product → select product → set trigger |
| **Define quality checks per picking type** | Inspection Point → Control Type = Picking → select picking type |
| **Batch-close checks** | Quality Checks → select multiple → Action → Confirm |
| **Print NC report** | Open non-conformity → Print → Non-Conformity Report |
| **Link NC to a corrective action** | Non-Conformity → Actions tab → create / link action |

---

## 6. Tips & Best Practices

- **Naming convention**: Use prefixes like `[RCV]` for receipt inspections, `[MO]` for manufacturing checks to keep inspection points organized.
- **Quantitative limits**: Define a **tolerance range** (Min / Max) so the system auto-computes pass/fail.
- **Inspection frequency**: Use the **Frequency** field on the inspection point (e.g. every 3rd receipt) to reduce overhead.
- **Team assignment**: Create dedicated quality teams (e.g. *Incoming QC*, *Production QC*) for proper assignment.
- **Audit trail**: Every check is time-stamped with the user who performed it – no need for paper logs.

---

## 7. Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| Check not created on picking validation | Inspection point not linked to the picking type or product | Verify the inspection point's Picking Type / Product and Trigger fields |
| Cannot confirm a check | User lacks Quality / Manager rights | Check user access rights in Settings → Users → Access Rights |
| Non-conformity not visible | Filter set to *Draft* only | Remove draft filter or change to *All* |
| Quantitative check shows wrong pass/fail | Tolerance Min / Max not set | Edit inspection point and supply correct tolerance values |

---

*End of Quality Control User Guide*
