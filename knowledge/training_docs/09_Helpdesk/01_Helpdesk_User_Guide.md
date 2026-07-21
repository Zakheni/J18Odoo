# Odoo 18 Helpdesk – End-User Manual

**Module Version:** Odoo 18 Enterprise  
**Document Type:** Training Manual  
**Audience:** Helpdesk Agents, Team Leads, Portal Users

---

## Table of Contents

1. [Overview](#1-overview)
2. [Accessing the Helpdesk Module](#2-accessing-the-helpdesk-module)
3. [Creating Tickets](#3-creating-tickets)
4. [Ticket Stages & Kanban Workflow](#4-ticket-stages--kanban-workflow)
5. [Priorities & Categories](#5-priorities--categories)
6. [Assigning Tickets & Team Routing](#6-assigning-tickets--team-routing)
7. [SLA Management](#7-sla-management)
8. [Customer Communication](#8-customer-communication)
9. [Timesheets on Tickets](#9-timesheets-on-tickets)
10. [Reporting & Dashboards](#10-reporting--dashboards)
11. [Common Daily Workflows](#11-common-daily-workflows)
12. [Tips & Best Practices](#12-tips--best-practices)

---

## 1. Overview

The Odoo 18 Helpdesk module is a **centralized ticket management system** that lets your team track, prioritize, and resolve customer requests. Tickets can arrive from multiple channels — customer portal, email, or manual creation by an agent — and flow through configurable stages with SLA monitoring.

**Key capabilities:**
- Multi-channel ticket intake (portal, email, manual)
- Kanban / list / pivot / graph views
- Automated team routing and assignment
- Service Level Agreement (SLA) tracking with timers
- Integrated customer communication (chatter, email gateway, portal)
- Timesheet logging against tickets
- Real-time dashboards and reporting

---

## 2. Accessing the Helpdesk Module

1. Log in to Odoo 18 with your credentials.
2. From the **Apps** menu (or the App Switcher icon in the top-left corner), select **Helpdesk**.
   - If you do not see the Helpdesk icon, ask your administrator to install the *Helpdesk* module.
3. The Helpdesk dashboard opens, displaying a summary of tickets, SLA statuses, and your team's performance.

> **💡 Tip:** Bookmark `/web#action=helpdesk_dashboard` for quick access.

---

## 3. Creating Tickets

Tickets can be created in three ways:

### 3.1 Manual Creation (Agent)

1. From the Helpdesk dashboard, click **New**.
2. Fill in the required fields:
   - **Subject** – Short title of the issue.
   - **Customer** – Search and select an existing contact, or create a new one by typing a new name and pressing "Create".
   - **Team** – Select the helpdesk team responsible (auto-set if a default team exists).
3. Optional fields:
   - **Category**, **Priority**, **Tags**, **Description**.
4. Click **Save** or **Save & Close**.

> **💡 Tip:** Use the **Description** field to paste the full customer email or issue log; the Chatter is better for ongoing updates.

### 3.2 Portal Creation (Customer-Submitted)

Customers can create tickets directly from the **Customer Portal**:

1. Customer logs into `https://<yourdomain>.odoo.com/my/home`.
2. Under **Helpdesk**, they click **New Ticket**.
3. They fill in:
   - Subject
   - Description of the issue
   - (Optional) Attachments
4. The ticket is automatically routed to the correct team (based on the portal user's company / team rules).
5. The agent receives a notification and can begin working.

> **💡 Tip:** To enable portal access, go to *Helpdesk > Configuration > Settings* and check *Customer Portal*.

### 3.3 Email Integration (Alias)

If email aliases are configured:

1. Customer sends an email to `support@<yourdomain>.com`.
2. Odoo automatically creates a ticket in the corresponding helpdesk team.
3. The email body becomes the **Description**; attachments are added as notes.
4. Replies from the agent (via Chatter) are delivered back to the customer by email.

> **💡 Tip:** Set up multiple aliases for different teams, for example:  
> `sales@` → Sales Support team, `tech@` → Technical Support team.

---

## 4. Ticket Stages & Kanban Workflow

Tickets move through **stages** that represent their lifecycle. Default stages:

| Stage       | Purpose                                     |
|-------------|---------------------------------------------|
| New         | Recently created, not yet triaged           |
| In Progress | Agent is actively working on the ticket     |
| Waiting     | Awaiting customer reply or third-party input|
| Resolved    | Solution provided; awaiting customer confirmation |
| Closed      | Confirmed resolved; no further action needed|

### Working with Stages

1. Open the **Helpdesk > Tickets** menu.
2. Switch to **Kanban** view (top-right icon grid).
3. Drag and drop a ticket card from one column to another to update its stage.
4. Alternatively, open a ticket → edit the **Stage** field in the form header.

> **💡 Tip:** Your administrator can customize stage names, add stages (e.g., "Escalated"), and define **folded stages** (stages hidden from the kanban by default, such as "Closed").

---

## 5. Priorities & Categories

### 5.1 Priorities

Used to indicate urgency. Click the priority stars on the ticket form or kanban card:

| Stars | Label      | Meaning                                      |
|-------|------------|----------------------------------------------|
| 0     | Not urgent | Low impact; can be scheduled                 |
| 1     | Low        | Minor issue                                  |
| 2     | Medium     | Standard priority                            |
| 3     | High       | Important; needs prompt attention            |
| 4     | Urgent     | Critical; immediate action required          |

### 5.2 Categories

Categories help classify tickets for reporting and routing:

1. Go to **Helpdesk > Configuration > Categories**.
2. Categories are hierarchical (parent / child).
3. Each category can be linked to a specific **team** — tickets with that category are auto-routed to that team.
4. Example categories: *Billing*, *Technical Issue*, *Feature Request*, *Account Access*.

> **💡 Tip:** Use the **Internal Notes** tab on a category to document handling instructions for agents.

---

## 6. Assigning Tickets & Team Routing

### 6.1 Manual Assignment

1. Open a ticket.
2. In the **Assigned To** field, search for a user (agent) and select them.
3. The agent receives an inbox notification and an email (if configured).

### 6.2 Automatic Assignment Rules

Administrators can set up **Assignment Rules** under *Helpdesk > Configuration > Assignment Rules*:

- **Round Robin** – Each new ticket goes to the next agent in a predefined list.
- **Load Sharing** – Ticket is assigned to the agent with the fewest open tickets.
- **Based on Category** – Certain categories are automatically routed to specific teams or agents.

> **💡 Tip:** Assignment rules are evaluated in order. The first matching rule is applied.

### 6.3 Team Routing

Each ticket belongs to a **Helpdesk Team**. Teams define:
- Default stages
- SLA policies
- Assignment rules
- Email aliases

To switch a ticket's team: edit the ticket → change the **Team** field → click **Save**. Stages and SLAs update accordingly.

---

## 7. SLA Management

SLA (Service Level Agreement) policies set time-based targets for ticket resolution.

### 7.1 How SLAs Work

1. Each **SLA Policy** is defined under *Helpdesk > Configuration > SLA Policies*.
2. A policy contains **SLA Items** — each item is a rule with:
   - **Target Stage** – e.g., "In Progress" or "Closed"
   - **Time** – e.g., 4 hours, 1 day
   - **Conditions** – e.g., priority = "High" AND category = "Technical Issue"
3. When a ticket matches an SLA item's conditions, a timer starts.
4. The SLA deadline is shown on the ticket form and kanban cards.

### 7.2 Monitoring SLA Status

In the ticket list/kanban, each card shows:

- **On time** – Green indicator
- **At risk** – Yellow indicator (e.g., when 80% of time has elapsed)
- **Overdue** – Red indicator

> **💡 Tip:** Use the **SLA Status** filter in the search bar to quickly find overdue tickets: filter by *SLA Status > Overdue*.

### 7.3 Reaching SLA Target

To mark an SLA item as **Reached**, the ticket must reach the specified **Target Stage** within the time limit. Once reached, the timer stops and the SLA indicator turns green permanently for that item.

---

## 8. Customer Communication

### 8.1 Chatter (Internal & External)

Every ticket has a **Chatter** (bottom of the form). Use it to:

- **Send a message** – Type in the text box and press Enter. If the customer has an email address, the message is sent via email.
- **Log a note** – Check *Internal Note* so the message is visible only to agents.
- **Schedule an activity** – Click the clock icon and set a reminder (e.g., "Follow up in 2 hours").
- **Attach files** – Drag & drop files into the chatter.

> **💡 Tip:** Use **@mentions** in chatter messages to notify specific colleagues: type `@` followed by their name.

### 8.2 Email Gateway

When the email integration is active:

- Incoming emails automatically create tickets (see §3.3).
- Outgoing chatter replies are sent from the team's email alias.
- The full email thread is preserved in the chatter as a threaded conversation.

### 8.3 Customer Portal

Customers can:

1. Log in to the portal at `https://<yourdomain>.odoo.com/my/home`.
2. View their submitted tickets and their **stage**.
3. Add messages and attachments to existing tickets.
4. Close tickets when they are satisfied.

> **💡 Tip:** Encourage customers to use the portal for follow-ups so that the conversation history is centralized in Odoo rather than scattered across personal inboxes.

---

## 9. Timesheets on Tickets

If the *Helpdesk Timesheets* feature is enabled, agents can log time directly on tickets.

### Logging Time

1. Open a ticket.
2. Go to the **Timesheets** tab (between Chatter and Other tabs).
3. Click **Add a line**.
4. Fill in:
   - **Date** (defaults to today)
   - **Description** of the work done
   - **Duration** in hours or days
5. Click **Save**.

### Timesheet Reporting

- Navigate to **Helpdesk > Reporting > Timesheets**.
- See total hours per ticket, per customer, per agent, or per team.
- Use pivot or graph views to analyze workload and billable hours.

> **💡 Tip:** If timesheets are linked to the **Project** module, hours logged on a ticket can also appear in the associated project's timesheet grid.

---

## 10. Reporting & Dashboards

### 10.1 Helpdesk Dashboard

The main dashboard (click **Helpdesk** in the top menu) displays:

- **Tickets to close** – Tickets in "Resolved" stage awaiting confirmation.
- **New tickets** – Unassigned, recently created tickets.
- **My tickets** – Tickets assigned to you.
- **Overdue SLAs** – SLA failures requiring immediate attention.
- **SLA Performance** – Percentage of tickets meeting SLA targets (last 30 days).

### 10.2 Pivot & Graph Views

1. Go to **Helpdesk > Reporting > Tickets**.
2. Switch between **Pivot**, **Graph**, and **Cohort** views using the icons at the top-right.
3. **Pivot** – Drag measures (e.g., Ticket Count) and dimensions (e.g., Team, Category, Priority) into rows / columns.
4. **Graph** – Choose bar, line, pie, or donut charts.

Common analyses:

| Question                               | Pivot Setup                                           |
|----------------------------------------|-------------------------------------------------------|
| How many tickets per team this month?  | Rows: Team; Columns: Month; Measure: Count            |
| Which category has the most tickets?   | Rows: Category; Measure: Count                        |
| What is the average resolution time?   | Measure: Average Hours to Close                       |
| SLA breach rate per agent?             | Rows: Assigned To; Columns: SLA Status; Measure: Count|

> **💡 Tip:** Click the **📊 Measures** button to add computed fields like *Average Hours to Close* or *Days to Close*.

### 10.3 Custom Dashboards

Administrators can create custom dashboards using the **Dashboard** app:

- Add an **Embedded Dashboard** view from within Helpdesk.
- Combine Helpdesk data with data from Sales, Project, or other apps.

---

## 11. Common Daily Workflows

### 11.1 Morning Triage (Start of Day)

1. Open **Helpdesk > Dashboard**.
2. Review the **New Tickets** column — check for any overnight submissions.
3. For each new ticket:
   - Verify the **Customer** and **Category**.
   - Set the **Priority** based on urgency.
   - **Assign** to yourself or a team member.
4. Check the **Overdue SLA** list — resolve or escalate these first.
5. Review tickets in **Waiting** stage — send follow-up messages to customers who have not replied.

### 11.2 Processing a Ticket

1. Open a ticket from your queue.
2. Read the description and any chatter history.
3. Perform the required work (investigation, configuration, etc.).
4. Log a **Timesheet** entry if time tracking is used.
5. Update the chatter with your findings or next steps.
6. If waiting on the customer, move the ticket to **Waiting**.
7. If resolved, move to **Resolved** and add a resolution summary in the chatter.

### 11.3 Closing Tickets (End of Day)

1. Filter tickets: *Stage = Resolved* and *Assigned To = Me*.
2. If the customer confirmed resolution, move to **Closed**.
3. If the customer reopened the issue, move back to **In Progress** and continue working.
4. Review any **SLA breaches** and document the reason in an internal note.

### 11.4 Escalating a Ticket

1. If the issue cannot be resolved at your level:
   - Add an internal note explaining the escalation reason.
   - Use the **Assigned To** field or change the **Team** to the escalation team.
   - Optionally, schedule an **Activity** to ensure follow-up.
2. Notify the receiving agent via `@mention` in the chatter.

---

## 12. Tips & Best Practices

| Practice                          | Why                                                           |
|------------------------------------|---------------------------------------------------------------|
| Set correct priority immediately   | Drives SLAs, assignment rules, and dashboard filters.         |
| Keep chatter messages professional | They are visible to the customer (unless marked internal).    |
| Use categories consistently        | Enables accurate reporting and automated team routing.        |
| Log timesheets daily               | Avoids forgotten time entries and improves billing accuracy.  |
| Move tickets out of "New" quickly  | Reduces SLA risk and improves customer satisfaction.          |
| Close resolved tickets promptly    | Keeps your kanban clean and metrics accurate.                 |
| Use the **Waiting** stage          | Stops the SLA clock and signals blockers to your team.        |
| Set up email signatures            | Configured under *Settings > General Settings* for professional replies. |

---

## Appendix A: Keyboard Shortcuts

| Shortcut               | Action                   |
|------------------------|--------------------------|
| `Ctrl + Enter`         | Send message in chatter  |
| `Alt + T`              | Open ticket list         |
| `Alt + N`              | Create new ticket        |
| `Alt + S`              | Save current ticket      |
| `Esc`                  | Close sidebar / discard  |

---

## Appendix B: Glossary

| Term               | Definition                                                  |
|--------------------|-------------------------------------------------------------|
| Ticket             | A single customer request or issue.                         |
| Stage              | Step in the ticket lifecycle (New, In Progress, etc.).      |
| SLA                | Service Level Agreement — time target for resolution.       |
| SLA Item           | A specific rule defining conditions and target time.        |
| Chatter            | Real-time communication log on each record.                 |
| Portal             | Customer-facing website where clients track their tickets.  |
| Team               | Group of agents handling tickets for a specific area.       |
| Assignment Rule    | Automated logic that assigns tickets to agents.             |
| Kanban             | Visual board view showing tickets as cards in columns.      |

---

*End of Document — Odoo 18 Helpdesk User Guide v1.0*
