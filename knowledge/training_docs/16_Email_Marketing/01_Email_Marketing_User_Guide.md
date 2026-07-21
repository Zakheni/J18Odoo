# Email Marketing — User Guide

**Odoo 18 | Module: Email Marketing (mass_mailing)**

---

## Table of Contents

1. [Overview](#1-overview)
2. [Creating Email Campaigns](#2-creating-email-campaigns)
3. [Mailing Lists & Recipient Management](#3-mailing-lists--recipient-management)
4. [Designing Email Templates](#4-designing-email-templates)
5. [Drip Campaigns & Automation](#5-drip-campaigns--automation)
6. [A/B Testing](#6-ab-testing)
7. [Reporting: Opens, Clicks, Bounces](#7-reporting-opens-clicks-bounces)
8. [Lead Scoring from Campaigns](#8-lead-scoring-from-campaigns)

---

## 1. Overview

The **Email Marketing** module lets you design, send, and track **mass mailings** and **multi-step campaigns** directly inside Odoo. It integrates with Contacts, Sales (CRM), Marketing Automation, and Social Marketing.

### Key Concepts

| Term | Meaning |
|------|---------|
| **Mailing** | A one-shot email sent to a list of recipients. |
| **Campaign** | A container that groups one or more mailings for reporting. |
| **Drip Campaign** | An automated sequence of emails triggered by time delays or recipient actions. |
| **Mailing List** | A named set of contacts you send to. |
| **Blacklist** | Contacts who have unsubscribed or bounced — Odoo never sends to them. |

---

## 2. Creating Email Campaigns

### 2.1 Create a Campaign

1. Go to **Email Marketing → Campaigns → Campaigns**.
2. Click **New**.
3. Fill in:
   - **Campaign Name** — e.g., *Summer Sale 2026*.
   - **Company** — leave blank to share across companies.
   - **Responsible** — the user owning the campaign.
   - **Stage** — draft / in progress / done.
4. Click **Save**.

### 2.2 Add Mailings to a Campaign

1. From the campaign form, scroll to the **Mailings** tab.
2. Click **Add a line**.
3. Choose an existing mailing or create a new one.
4. Set the **schedule date** if you want to send later.

> **Tip:** You can also create a mailing first and link it to a campaign via the *Campaign* field on the mailing form.

### 2.3 Campaign Stages & Pipelines

Use the **Kanban** view to drag mailings through stages:

- **Draft** — not ready.
- **In Progress** — sending or scheduled.
- **Done** — all mailings finished.
- **Cancelled** — aborted.

You can customize stages under **Configuration → Campaign Stages**.

---

## 3. Mailing Lists & Recipient Management

### 3.1 Create a Mailing List

1. Go to **Email Marketing → Mailing Lists → Mailing Lists**.
2. Click **New**.
3. Enter:
   - **List Name** — e.g., *Newsletter Subscribers*.
   - **Active** — check to allow sending to this list.
4. Optionally, add a **Synced Mailing List** to auto-sync with external platforms (Mailchimp, SendGrid, etc.).

### 3.2 Add Recipients

From the list form, click the **Recipients** tab and click **Add**. You can also import:

1. Click **Import** (top-right).
2. Upload a CSV with columns: `email`, `name`, `phone`, etc.
3. Map fields and confirm.

### 3.3 Use Mailing List as Target

When creating a mailing, choose **Mailing List** as the *Recipient* type and pick your list.

### 3.4 Suppression / Blacklist

- Odoo automatically blacklists recipients who:
  - Click **Unsubscribe** in an email.
  - Hard-bounce (permanent delivery failure).
- View blacklisted contacts at **Email Marketing → Configuration → Blacklisted Email Addresses**.
- You can manually add addresses to the blacklist via **Email Marketing → Configuration → Blacklisted Email Addresses**.

> **Tip:** To remove an address from the blacklist, archive its blacklist record.

---

## 4. Designing Email Templates

### 4.1 Create a New Template

1. Go to **Email Marketing → Mailings → Templates**.
2. Click **New**.
3. Choose a layout:
   - **Plain Text** — simple text-only email.
   - **Bootstrap Grid** — responsive drag-and-drop editor (recommended).
4. Build your content with the **rich text / block editor**:
   - Add images, buttons, dividers, social links.
   - Use **dynamic placeholders** (see below).

### 4.2 Dynamic Placeholders (Variables)

Insert variables that Odoo replaces per recipient:

| Placeholder | Replaced With |
|-------------|---------------|
| `{{ object.name }}` | Contact's name |
| `{{ object.email }}` | Contact's email |
| `{{ object.company_name }}` | Company (if set) |
| `{{ unsubscribe_url }}` | One-click unsubscribe link |
| `{{ opt_out_url }}` | Opt-out link (web page) |
| `{{ link_for:my_link }}` | Trackable link |

> **Tip:** Always include `{{ unsubscribe_url }}` or `{{ opt_out_url }}` to comply with anti-spam laws (CAN-SPAM / GDPR).

### 4.3 Upload Images

1. In the editor, click **Image** block.
2. Upload from your computer or pick from the media library.
3. Odoo automatically hosts images.

### 4.4 Save as Template

Once designed, click **Save** to reuse the design in other mailings.

---

## 5. Drip Campaigns & Automation

Drip campaigns send a sequence of emails automatically based on time delays or recipient actions.

### 5.1 Enable Marketing Automation

Ensure the **Marketing Automation** module is installed (Apps → Marketing Automation).

### 5.2 Create a Drip Campaign

1. Go to **Marketing Automation → Campaigns → Campaigns**.
2. Click **New**.
3. Set the **Target Model** — choose *Mailing Contact* to use mailing lists.
4. Define **Participants** — typically a mailing list.
5. Add **Activities** (email steps):

#### Add an Email Step

1. In the *Activities* tab, click **Add an activity**.
2. Choose **Send Email**.
3. Select the **Email Template** (designed earlier).
4. Set **Trigger**:
   - *On entry* — sends immediately when contact enters the campaign.
   - *X days after previous activity* — time delay.
   - *After a specific date field* — use a date on the contact record.
5. Click **Save**.

### 5.3 Action-Based Triggers

Create branches based on recipient behaviour:

- **Add a Condition** — check if a recipient has opened or clicked an email.
  - *Email Opened?* → send follow-up.
  - *Not opened?* → send re-engagement.
- **Add a Filter** — e.g., only continue if `country_id == US`.

### 5.4 Start the Automation

1. Click **Start** on the campaign.
2. Participants are added automatically as they match the target criteria.
3. Odoo sends emails based on the activity schedule.

> **Tip:** Use the **Test** button on individual activities to preview the email before launch.

---

## 6. A/B Testing

A/B testing lets you send two variants of the same email to a small sample, then automatically send the winner to the rest.

### 6.1 Set Up an A/B Test

1. Go to **Email Marketing → Mailings → Mailings**.
2. Click **New** and fill in the basic info.
3. Set **Mailing Type** to *Mass Mailing*.
4. Under the **A/B Testing** tab, check **Enable A/B Test**.
5. Configure:
   - **Test Ratio** (percentage of recipients in test) — e.g., 20%.
   - **Test Metric** — *Open Rate* or *Click-Through Rate*.
   - **Winner Selection** — *Manual* or *Automatic*.
   - **Test Duration** — how long to wait before declaring a winner (e.g., 4 hours).

### 6.2 Create Variants

1. In the **Variants** tab, you already have *Variant A*.
2. Click **Add a Variant** to create *Variant B*.
3. Edit each variant's subject, body, or template independently.

### 6.3 Launch & Monitor

1. Click **Send / Schedule**.
2. Odoo sends the test batches.
3. When the test duration passes:
   - **Manual**: Review stats and click **Set as Winner** on the leading variant.
   - **Automatic**: Odoo sends the winner to the remaining recipients.

> **Tip:** Only change **one variable** at a time (subject line OR image OR CTA) for statistically meaningful results.

---

## 7. Reporting: Opens, Clicks, Bounces

### 7.1 Mailing Dashboard

After sending, open the mailing form to see the **Statistics** tab:

| Metric | Description |
|--------|-------------|
| **Total Sent** | Emails successfully dispatched. |
| **Delivered** | Confirmed delivered (no bounce). |
| **Opened** | Unique opens (tracked via invisible pixel). |
| **Clicked** | Unique clicks on tracked links. |
| **Replied** | Replies received (if tracking is enabled). |
| **Bounced** | Permanent (hard) + temporary (soft) bounces. |
| **Unsubscribed** | Recipients who clicked unsubscribe. |

### 7.2 Campaign Reporting

1. Go to **Email Marketing → Reporting → Campaigns** (Pivot view) or **Campaigns Analysis** (Graph view).
2. Group by:
   - Campaign
   - Mailing
   - Sending date
   - List
3. Hover over chart segments to drill into raw data.

### 7.3 Individual Recipient Activity

1. Open the **Mailing** → **Recipients** tab.
2. Click a recipient line to see their **Status** and **Tracking**:
   - *Sent*
   - *Opened*
   - *Clicked*
   - *Bounced*
   - *Unsubscribed*

### 7.4 Export Reports

Click the **action gear (⚙) → Export All Records** to download raw CSV/Excel data.

### 7.5 Bounce Handling

- **Hard Bounces** — invalid email, domain not found. Recipient is automatically blacklisted.
- **Soft Bounces** — mailbox full, temporary server issue. Odoo retries up to 3 times; after repeated soft bounces the address may be blacklisted.

Review bounce details via **Email Marketing → Configuration → Blacklisted Email Addresses**.

> **Tip:** Keep your lists clean by periodically exporting bounced contacts and removing them from your mailing lists.

---

## 8. Lead Scoring from Campaigns

Email engagement can automatically adjust lead / opportunity scores when the **CRM** module is installed.

### 8.1 Enable Lead Scoring

1. Go to **CRM → Configuration → Settings**.
2. Scroll to **Lead Scoring**.
3. Set scores for:
   - **Email Opened** — e.g., +2 points.
   - **Email Clicked** — e.g., +5 points.
   - **Email Replied** — e.g., +10 points.

### 8.2 How Scoring Works

- When a contact (linked to a lead/opportunity) opens an email, Odoo adds points automatically.
- The score appears as **Scoring** (numeric) and **Automated Score** on the lead form.
- You can set **Score-Based Segregation** — e.g., automatically move leads above 50 points to *Qualified* stage.

### 8.3 View Score History

1. Open a lead or opportunity.
2. Go to the **Scoring** tab.
3. Each email action is logged with a timestamp and point change.

### 8.4 Lead Scoring from Marketing Automation

In a drip campaign, add a **Update Lead Score** activity:

1. Edit your campaign activity.
2. Choose *Update Lead Score* action.
3. Enter the number of points (can be positive or negative).
4. The lead/opportunity linked to the mailing contact gets the score modification.

> **Tip:** Use negative scores to deprioritise cold leads — e.g., -5 if a contact hasn't opened any email in 90 days.

---

## Appendix: Best Practices

| Area | Recommendation |
|------|----------------|
| **List Hygiene** | Remove inactive subscribers every 3 months. |
| **Subject Line** | Keep under 60 characters; avoid spammy words. |
| **Send Time** | Test different days/hours; Tuesday–Thursday 10 AM–2 PM often performs best. |
| **Mobile** | Use the responsive editor and preview on mobile before sending. |
| **Unsubscribe** | Prominently display an unsubscribe link — legally required in most countries. |
| **A/B Tests** | Use at least 1 000 recipients in the test group for statistical significance. |
| **Frequency** | 1–2 emails per week maximum to prevent list fatigue. |
| **GDPR** | Store consent date and source on the contact form; include privacy policy link. |

---

*End of guide — Odoo 18 Email Marketing*

*For more help, visit the Odoo documentation at https://www.odoo.com/documentation/18.0/applications/marketing/email_marketing.html*
