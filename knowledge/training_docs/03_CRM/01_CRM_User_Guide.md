# Odoo 18 CRM Module — End-User Manual

> **Applies to:** Odoo 18 Enterprise  
> **Document version:** 1.0  
> **Objective:** This guide explains how to use the CRM module to track leads, manage the sales pipeline, and close opportunities.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Leads vs. Opportunities](#2-leads-vs-opportunities)
3. [Pipeline Management](#3-pipeline-management)
4. [Sales Teams](#4-sales-teams)
5. [Activities & Scheduling](#5-activities--scheduling)
6. [Communication](#6-communication)
7. [Reporting](#7-reporting)
8. [Lead Enrichment (IAP)](#8-lead-enrichment-iap)
9. [Common Workflows](#9-common-workflows)
10. [Glossary](#10-glossary)

---

## 1. Overview

The **CRM (Customer Relationship Management)** module is the central hub for managing your sales process from first contact to signed deal. It helps you:

- **Track leads** — capture every inbound inquiry from the website, email, phone, or live chat.
- **Manage the pipeline** — visualise every deal on a Kanban board, move it through stages, and update its value.
- **Close opportunities** — convert qualified leads into won deals with accurate revenue tracking.
- **Measure performance** — use built-in dashboards and reports to forecast revenue, analyse win/loss ratios, and monitor team targets.

### Key Concepts

| Concept | Description |
|---|---|
| **Lead** | An unqualified inquiry. Limited data is known (e.g., just a name and email). |
| **Opportunity** | A qualified, sales-ready deal with expected revenue, probability, and a closing date. |
| **Pipeline Stage** | A step in the sales process (e.g., *New*, *Qualified*, *Proposal Sent*, *Won*). |
| **Sales Team** | A group of salespeople who share a pipeline, targets, and assignment rules. |
| **Activity** | A scheduled action such as a call, meeting, or to-do linked to a record. |
| **Chatter** | The collaboration widget at the bottom of every record for internal notes, emails, and attachments. |

---

## 2. Leads vs. Opportunities

### What is a Lead?

A **lead** is an early-stage, unqualified contact. Leads typically come from:

- Website contact forms
- Live chat conversations
- Mass-imported contact lists
- The **CRM IAP Mine** tool (purchased lead lists)

**Characteristics:**

- Minimal required fields (name and email are often enough).
- No expected revenue or probability is set.
- Can be created by anyone, including automated processes.

### What is an Opportunity?

An **opportunity** is a qualified deal that you intend to pursue. It represents a real sales conversation with a concrete monetary value.

**Characteristics:**

- Requires an **Expected Revenue**, **Probability**, and **Expected Closing Date**.
- Appears on the pipeline Kanban board.
- Can be assigned to a specific **Salesperson** and **Sales Team**.

### Converting a Lead to an Opportunity

1. Open the lead from the **Leads** menu.
2. Click the **Convert to Opportunity** button (top of the form).
3. A dialog appears with options:
   - **Merge with existing customer** — link the lead to an existing contact in Odoo.
   - **Create a new customer** — Odoo will create a new contact record automatically.
4. Optionally assign a **Salesperson** and **Sales Team** before confirming.
5. Click **Convert**.

> **Tip:** Once converted, the original lead is archived. All communication from the chatter is carried over to the new opportunity.

> **Warning:** Converting is a one-way action. You cannot revert an opportunity back to a lead. However, you can mark an opportunity as *Lost* if it does not progress.

---

## 3. Pipeline Management

### Accessing the Pipeline

Go to **CRM → Pipeline**. You will see the Kanban view by default, showing each stage as a column.

### Creating an Opportunity

**From Kanban view:**

1. Click **Create** (top-left).
2. Fill in:
   - **Opportunity Title** (required) — e.g., "Acme Corp — Q4 Software Deal".
   - **Customer** — start typing to search existing contacts or create a new one.
   - **Expected Revenue** — estimated deal value in your company currency.
   - **Probability** — as a percentage (e.g., 60%).
   - **Expected Closing Date** — the anticipated close month/date.
   - **Salesperson** — the person responsible for this deal.
   - **Sales Team** — the team this deal belongs to.
3. Click **Save**.

**From a lead (after conversion):**

The opportunity is auto-created; you only need to fill the revenue and probability fields if they were not carried over.

### Moving Through Stages (Kanban)

- **Drag and drop** an opportunity card from one column to the next.
- A confirmation dialog may appear if the stage requires extra information — fill it in and confirm.
- The **Probability** is automatically updated if the stage has a default probability configured (set by the administrator in **CRM → Configuration → Stages**).

### Editing Expected Revenue, Probability, and Closing Date

**Quick edit on Kanban:**

1. Click the pencil icon on the opportunity card.
2. Update **Expected Revenue**, **Probability**, or **Expected Closing**.
3. Press **Enter** or click outside the field to save.

**Full edit on the form:**

1. Click the opportunity card to open the form view.
2. Edit any field in the **Opportunity** tab.
3. Click **Save**.

### Assigning Team Members

1. Open the opportunity.
2. In the **Salesperson** field, select a user from the dropdown.
3. The **Sales Team** will auto-populate if the user belongs to one, or you can set it manually.

> **Tip:** Use the **My Pipeline** filter (top-right of the Kanban) to see only your assigned opportunities.

### Stage-Dependent Features

- **Stage Folds** — If a stage is configured as *folded*, opportunities in that stage are hidden from the default Kanban view (useful for *Won/Lost* stages).
- **Required Fields per Stage** — Administrators can require certain fields before moving to the next stage (e.g., require expected revenue before moving to *Proposal Sent*).

---

## 4. Sales Teams

### How Sales Teams Work

- Each **Sales Team** has its own pipeline, targets, and members.
- Team members can be assigned opportunities manually or automatically via **assignment rules**.
- Team leaders can monitor their team's progress on a dedicated dashboard.

### Viewing Teams

Go to **CRM → Configuration → Sales Teams**.

| Field | Description |
|---|---|
| **Team Name** | The name of the team. |
| **Team Leader** | The user responsible for the team. |
| **Members** | List of salespeople in the team. |
| **Target (Invoiced)** | Invoiced revenue target for a period. |
| **Target (Won)** | Number of won deals target. |

### Team Assignment Rules

Administrators can configure automatic lead/opportunity assignment:

1. Go to **CRM → Configuration → Sales Teams**.
2. Open a team.
3. In the **Assignment** tab, choose:
   - **Manual** — a leader manually assigns each deal.
   - **Automatic** — new leads are distributed round-robin or by lowest workload.

> **Tip:** Assignment rules only apply to newly created leads/opportunities, not existing ones.

### Team Targets

Team leaders and managers can view target achievement:

- **CRM → Reporting → Dashboard** shows a team-by-team comparison.
- Each team member’s **won deals** and **invoiced revenue** are matched against the configured targets.

> **Tip:** Targets are set per period (month/quarter/year). Check the **Period** filter on the dashboard.

---

## 5. Activities & Scheduling

### What are Activities?

Activities are scheduled actions linked to a lead or opportunity. Types include:

- **Call** — log a phone call.
- **Meeting** — schedule an Odoo Calendar event.
- **To-Do** — a follow-up task.
- **Email** — send an email (opens the composer).

### Adding an Activity

1. Open a lead or opportunity.
2. In the **Activities** widget (top-right of the form), click **Schedule an Activity** (clock icon).
3. Fill in:
   - **Activity Type** — Call, Meeting, To-Do, etc.
   - **Summary** — a short title (e.g., "Follow up on pricing").
   - **Due Date** — when the activity must be completed.
   - **Assigned To** — the responsible person (defaults to the record's salesperson).
   - **Note** — any additional details.
4. Click **Schedule**.

### Marking Activities as Done

- In the **Activities** widget, hover over the activity and click the **Mark Done** checkmark.
- You can add a **log note** summarising the outcome before confirming.

### Viewing All Activities

Go to **CRM → Reporting → Activities** for a full list of pending and overdue activities across all teams.

> **Warning:** Overdue activities appear in red on the widget. Regularly review them to avoid stalled deals.

### Logging a Call without Scheduling

1. Click the **Log a Call** button on the opportunity form.
2. Enter a summary and a detailed note.
3. Click **Log**. This creates a completed activity and adds a message to the chatter.

---

## 6. Communication

### The Chatter

Every lead and opportunity has a **chatter** at the bottom of the form. Use it to:

- **Add internal notes** — type in the field and select **Send & Close** (internal only).
- **Log emails** — the chatter automatically captures incoming/outgoing emails linked to the contact.
- **Attach files** — drag and drop documents, quotes, or proposals.
- **Send messages** — type a message and click **Send** to post it to the chatter (visible to all users with access).

### Sending Emails from an Opportunity

1. Open the opportunity.
2. Click **Send Email** (top of the form).
3. The composer pre-fills the customer's email address.
4. Write your subject and body (use the rich-text editor).
5. Click **Send**.

> **Tip:** Email templates can be pre-configured by your administrator. Click **Template** to select one.

### SMS Messaging

If the **CRM SMS** module is installed:

1. Open a lead or opportunity.
2. Click **Send SMS** (top of the form, visible when the customer has a mobile number).
3. Compose your message (limited to 160 characters per SMS).
4. Click **Send**.

> **Tip:** SMS credits must be purchased via IAP. Go to **Settings → IAP → SMS** to check your balance.

> **Warning:** SMS is billed per message. Long messages are split into multiple parts and billed accordingly.

### Live Chat (Website)

If the **CRM Livechat** module is installed:

- Website visitors can initiate a chat with the sales team.
- Chats are automatically converted into leads.
- The **Livechat Dashboard** (under **CRM**) lets you monitor active conversations.

### Email Plugin

If the **CRM Mail Plugin** is installed:

- Use the browser extension or Odoo Outlook add-in to sync emails and contacts.
- Emails sent from your inbox can be logged automatically to the matching lead/opportunity.
- The plugin can also create new leads from unknown senders.

---

## 7. Reporting

### Pipeline Analysis

1. Go to **CRM → Reporting → Pipeline Analysis**.
2. Use the pivot table to group by:
   - **Sales Team**
   - **Salesperson**
   - **Stage**
   - **Expected Closing Month**
3. Drag measures into the **Measures** area:
   - **Expected Revenue**
   - **Number of Opportunities**
   - **Probability Weighted Revenue**

### Dashboard

1. Go to **CRM → Reporting → Dashboard**.
2. Key widgets:
   - **My Pipeline** (your own opportunities by stage)
   - **Forecast** (sum of expected revenue, grouped by closing month)
   - **Won/Lost** (ratio and trend chart)
   - **Team Targets** (achieved vs. target for each team)
3. Use the date range and team filters to customise the view.

### Won / Lost Analysis

1. Go to **CRM → Reporting → Pipeline Analysis**.
2. Add a filter: **Stage is Won** or **Stage is Lost**.
3. Compare:
   - **Win rate** = (Won deals) × 100 ÷ (Won + Lost deals)
   - **Average deal size** for won opportunities.
   - **Time to close** (if your administrator has enabled the *Age* field).

> **Tip:** Export any report to Excel by clicking the **Export** button.

---

## 8. Lead Enrichment (IAP)

### CRM IAP Enrich

The **CRM IAP Enrich** service automatically enriches lead data using the contact's email address. It can fill in:

- Company name, size, and industry
- Job title and phone number
- Social media profiles (LinkedIn, Twitter)

**How to Enrich a Lead:**

1. Open a lead that has at least an email address.
2. Click the **Enrich** button (magic wand icon) in the top toolbar.
3. Odoo queries the IAP service. After a few seconds, the enriched data appears in the form.
4. Review and **Save** the changes.

**Batch Enrichment:**

1. Go to **CRM → Leads** and switch to **List** view.
2. Select the leads you want to enrich (checkboxes).
3. Click **Action → Enrich** (requires the *Enrich* option in the action menu).
4. Confirm. Credits are consumed per lead.

> **Warning:** Enrichment consumes IAP credits. Check your balance at **Settings → IAP → Account**.

> **Tip:** Set up an automated **Server Action** to enrich leads automatically when they reach a certain stage (requires technical rights).

### CRM IAP Mine (Lead Mining)

The **CRM IAP Mine** module lets you purchase leads from external data providers.

1. Go to **CRM → Lead Mining**.
2. Define your target:
   - **Industry** (e.g., Technology, Healthcare)
   - **Job Function** (e.g., CTO, VP of Sales)
   - **Company Size** (e.g., 50–200 employees)
   - **Location** (country, state, city)
3. Click **Search & Buy**.
4. A preview shows the number of matching leads and the cost in IAP credits.
5. Confirm the purchase. Leads are created in your **Leads** view.

> **Tip:** Start with a small batch to test the data quality before buying large lists.

> **Warning:** Purchased leads are non-refundable. Review the preview carefully.

---

## 9. Common Workflows

### Workflow A: From Lead to Won Deal

| Step | Action |
|---|---|
| 1 | A website visitor fills out the **Contact Us** form → a **Lead** is auto-created. |
| 2 | Salesperson opens the lead, clicks **Enrich** to pull company data. |
| 3 | Salesperson calls the lead and adds a note in the chatter. |
| 4 | Salesperson clicks **Convert to Opportunity**, links to an existing customer, and sets expected revenue to **$15,000 / 50%**. |
| 5 | The opportunity appears in the **New** stage of the pipeline. |
| 6 | Salesperson drags it to **Qualified** after a discovery call. |
| 7 | Salesperson schedules an **Activity: Meeting** to present a proposal. |
| 8 | After the meeting, drags to **Proposal Sent**. Updates probability to **75%**. |
| 9 | Customer accepts. Salesperson drags to **Won**. Confirms the **Actual Revenue** (if different from expected). |

### Workflow B: Handling a Lost Deal

1. Drag the opportunity to the **Lost** stage.
2. In the dialog, select a **Lost Reason** (e.g., *Budget too high*, *Competitor*, *Timing*).
3. Optionally enter a note explaining the loss.
4. Click **Confirm**. The pipeline analysis will reflect this in the win/loss report.

> **Tip:** Review lost reasons quarterly to identify patterns and adjust your sales strategy.

### Workflow C: Lead Mining & Assignment

1. Go to **CRM → Lead Mining**.
2. Set filters: Industry = *Manufacturing*, Location = *Germany*.
3. Buy 50 leads (costs 50 IAP credits).
4. Leads appear in the **Leads** view, unassigned.
5. The **Sales Team Leader** opens each lead, clicks **Convert to Opportunity**, and assigns a team member.
6. Team members receive a notification and begin working their new opportunities.

### Workflow D: Using Live Chat

1. A visitor goes to the website and clicks the **Chat** bubble.
2. They type a question. The chat is routed to an available operator.
3. The operator answers; the chat is logged and a **Lead** is created automatically.
4. After the conversation, the operator opens the lead and converts it to an opportunity.

### Workflow E: Logging an Email via the Mail Plugin

1. Install the Odoo Mail Plugin browser extension / Outlook add-in.
2. Compose an email in Gmail/Outlook to `john@acme.com`.
3. Click **Log in Odoo** in the plugin toolbar.
4. The plugin matches the email to the existing opportunity for Acme Corp.
5. The email appears in the opportunity's chatter.

---

## 10. Glossary

| Term | Definition |
|---|---|
| **IAP** | In-App Purchases — pay-per-use credits for enrichment and mining services. |
| **Kanban** | A visual board with columns representing pipeline stages. |
| **Lead** | An unqualified contact record. |
| **Opportunity** | A qualified, revenue-tracked deal in the pipeline. |
| **Pipeline** | The sequence of stages a deal passes through from creation to won/lost. |
| **Probability** | The estimated likelihood (%) of winning a deal. |
| **Sales Team** | A group of users who share a pipeline and targets. |
| **Stage** | A step in the sales process (e.g., New, Qualified, Won). |
| **Chatter** | The real-time collaboration area on every record. |
| **Expected Revenue** | The estimated monetary value of an opportunity. |

---

*End of Document*
