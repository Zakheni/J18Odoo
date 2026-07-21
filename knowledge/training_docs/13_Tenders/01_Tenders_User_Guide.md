# Zakheni Tender Management — End-User Manual

**Module:** zakheni_tender  
**Version:** 18.0.1.4.0  
**Author:** Zakheni ICT (Pty) Ltd  
**Applies to:** Odoo 18 Community & Enterprise

---

## Table of Contents

1. [Overview](#1-overview)
2. [Getting Started](#2-getting-started)
3. [Creating a Tender](#3-creating-a-tender)
4. [Tender Stages & Pipeline](#4-tender-stages--pipeline)
5. [Bid/No-Bid Analysis](#5-bidno-bid-analysis)
6. [Compliance Checking](#6-compliance-checking)
7. [AI Document Analysis](#7-ai-document-analysis)
8. [Tender Feeds & Discovery](#8-tender-feeds--discovery)
9. [Company Profiles & Auto-Matching](#9-company-profiles--auto-matching)
10. [Portal Access for Bidders](#10-portal-access-for-bidders)
11. [Dashboards & Reporting](#11-dashboards--reporting)
12. [Configuration & Administration](#12-configuration--administration)
13. [FAQ & Troubleshooting](#13-faq--troubleshooting)

---

## 1. Overview

The **Zakheni Tender Management** module lets you manage the full lifecycle of tenders and bids — from opportunity discovery and evaluation through to submission, award, and post-mortem analysis.

### Key capabilities at a glance

| Feature | Description |
|---------|-------------|
| **Pipeline management** | Kanban-based stages track each tender from *Identified → Reviewing → Preparing → Submitted → Under Evaluation → Won/Lost* |
| **Bid/No-Bid Analysis** | Weighted scoring framework (Strategic, Financial, Capacity, Competitive, Risk, Compliance) to decide whether to bid |
| **Compliance checklists** | Reusable templates with mandatory requirements; track compliance per tender |
| **AI document analysis** | Send tender documents to OpenAI, Anthropic, or a custom API to extract requirements, deadlines, risks, and bid recommendations |
| **Tender feed discovery** | Automatically fetch open tenders from South Africa's eTenders.gov.za OCDS API (free, no auth required) |
| **Profile matching** | Configure company profiles with service categories and keywords; NLP-based similarity scoring matches incoming tenders to your profile |
| **Portal access** | External bidders/issuers can view tender details and upload documents via the customer portal |
| **Dashboard & analysis** | Real-time KPI dashboard, pivot tables, graph views, and win/loss analysis |

> **💡 Tip:** The module is designed for organisations that regularly bid on tenders — particularly useful in South Africa where eTenders.gov.za is the primary public-sector procurement platform.

---

## 2. Getting Started

### 2.1 Navigation

After installation, a **Tenders** top menu appears in the main navigation bar with these submenus:

```
Tenders
├── Dashboard
├── Tender Feed
├── Tenders
├── Bid/No-Bid Analysis
├── Analysis
├── Compliance
│   ├── Checklists
│   └── Results
├── Matching
│   ├── Matches
│   └── Company Profiles
└── Configuration
    ├── Stages
    ├── Categories
    ├── Service Categories
    └── Preconfigured Keywords
```

### 2.2 Prerequisites

- **AI Analysis (optional):** Set an API key in *Settings → Technical → System Parameters*:
  - Key: `zakheni_tender.ai_api_key`
  - For custom API: also set `zakheni_tender.ai_custom_endpoint`
- **NLP Matching (optional):** Install the Python package `sentence-transformers` on your Odoo server for embedding-based similarity scoring.
- **Portal access:** Ensure the `portal` module is installed and your customer portal routes are configured.

---

## 3. Creating a Tender

### 3.1 Manual creation

**Step 1:** Go to **Tenders → Tenders** and click **New**.

**Step 2:** Fill in the core details:

| Field | Description |
|-------|-------------|
| **Tender Name** | A descriptive name for the opportunity (e.g. "SITA RFQ 123 — Network Equipment") |
| **Tender Reference** | The reference number assigned by the issuer |
| **Issuer** | The organisation publishing the tender (select or create a contact) |
| **Category** | Classify the tender (e.g. IT, Construction, Consulting) — configured under Configuration → Categories |
| **Responsible** | The user leading this bid (defaults to you) |
| **Team Members** | Additional colleagues working on the bid |

**Step 3:** Fill in the **Timeline** tab:

| Field | Purpose |
|-------|---------|
| **Publication Date** | When the tender was published |
| **Site Visit** | Scheduled site visit date/time |
| **Briefing Session** | Pre-bid briefing session |
| **Preparation Deadline** | Internal deadline to finish the proposal |
| **Submission Deadline** | **Critical** — drives alerts and deadline reminders |
| **Validity Period End** | How long the bid must remain valid |
| **Date Submitted** | When you actually submitted |
| **Award Date** | When the issuer announces the award |

**Step 4:** Fill in the **Financial** tab:

| Field | Purpose |
|-------|---------|
| **Estimated Tender Value** | The value indicated by the issuer (if known) |
| **Our Quoted Amount** | What you quoted |
| **Estimated Bid Cost** | Internal cost to prepare the bid |
| **Bid Bond Amount / Expiry / Bank** | Bid bond details |

**Step 5:** Click **Save**.

> **💡 Tip:** Use the chatter at the bottom of the form to log internal notes, upload related emails, and track activities.

### 3.2 Importing from the Tender Feed

See [Section 8 — Tender Feeds & Discovery](#8-tender-feeds--discovery). Feeds discovered from eTenders.gov.za can be imported as tenders with a single click.

---

## 4. Tender Stages & Pipeline

### 4.1 Default pipeline stages

When a tender is created, it starts in the **Identified** stage. The Kanban view shows the pipeline with these default stages:

| Stage | Sequence | Default Win % | Description |
|-------|----------|---------------|-------------|
| Identified | 10 | 5% | Opportunity spotted; initial review pending |
| Reviewing | 20 | 15% | Evaluating RFP documents |
| Preparing | 30 | 30% | Writing the proposal |
| Submitted | 40 | 50% | Bid submitted |
| Under Evaluation | 50 | 60% | Issuer evaluating bids |
| Won (folded) | 60 | 100% | Contract awarded |
| Lost (folded) | 70 | 0% | Unsuccessful |

> **💡 Tip:** Stages marked *Folded* (Won, Lost) collapse in the Kanban view when empty, keeping your active pipeline clean.

### 4.2 Using the Kanban pipeline

**Step 1:** Go to **Tenders → Tenders** and switch to **Kanban** view.

**Step 2:** Drag and drop a tender card from one stage to the next as the bid progresses.

**Step 3:** Update the **Win Probability (%)** as your confidence grows — this flows into pipeline value reporting.

**Step 4:** Use the status bar on the tender form to change stages with a single click.

### 4.3 Marking a result

When the issuer announces the outcome:

- Click **Mark Won** — the stage moves to *Won* and `Result = Won`
- Click **Mark Lost** — the stage moves to *Lost* and `Result = Lost`
- Click **Withdraw** — `Result = Withdrawn` (no stage change)

For lost tenders, complete the **Result** tab on the form with:
- **Competitors** — who won?
- **Reason Lost** — what went wrong? (feeds post-mortem analysis)

### 4.4 Calendar view

Switch to **Calendar** view to see all tender deadlines on a timeline — useful for capacity planning.

### 4.5 Configuring stages

Administrators can add/edit stages under **Configuration → Stages**. Each stage has:

- **Sequence** — controls order in the pipeline
- **Win Probability (%)** — default probability when a tender reaches this stage
- **Fold** — hide from Kanban when empty
- **Won/Lost** — marks terminal stages

> **💡 Tip:** Right-click on the Kanban column header to quickly add or edit stages.

---

## 5. Bid/No-Bid Analysis

Before committing resources to a bid, use the Bid/No-Bid analysis to score the opportunity against weighted criteria.

### 5.1 Starting an analysis

**Step 1:** Open any tender form.

**Step 2:** Click the **Bid/No-Bid** stat button in the top-right button box.

**Step 3:** A popup wizard opens with pre-set criteria across six categories:

| Category | Example Criteria |
|----------|------------------|
| Strategic Fit | Alignment with business strategy, Market presence |
| Financial | Estimated profitability, Bid cost vs return |
| Capacity & Resources | Team capacity, Skills available |
| Competitive Position | Differentiators, Past performance with issuer |
| Risk Assessment | Contractual risk, Delivery risk |
| Compliance | Mandatory requirements, B-BBEE scoring |

### 5.2 Scoring criteria

Each criterion has:
- **Weight** (1–5) — how important is this factor?
- **Score** (0–10) — how well does this tender score on this factor?

**Scoring guide:**

| Score | Meaning |
|-------|---------|
| 0–3 | Very poor / deal-breaker |
| 4–5 | Below average |
| 6–7 | Average / acceptable |
| 8–9 | Good / strong |
| 10 | Excellent / ideal |

### 5.3 Interpreting results

The system calculates automatically:

- **Total Score** = Σ (score × weight) for each criterion
- **Max Score** = Σ (10 × weight)
- **Score %** = (Total / Max) × 100

| Score % | Recommendation | Action |
|---------|---------------|--------|
| ≥ 70% | **Bid** | Proceed with proposal preparation |
| 40–69% | **Further Review** | Discuss with management; address weak areas |
| < 40% | **No-Bid** | Decline — resources better spent elsewhere |

### 5.4 Completing the analysis

Click **Complete Analysis** to finalise. The recommendation and score appear on the tender form for quick reference.

> **💡 Tip:** Click **Reopen** if you need to adjust scores after new information comes in.

---

## 6. Compliance Checking

Ensure your bid meets all mandatory requirements before submission.

### 6.1 Creating compliance checklists

**Step 1:** Go to **Tenders → Compliance → Checklists** and click **New**.

**Step 2:** Give the checklist a name (e.g. "SITA IT Tender Requirements").

**Step 3:** Optionally link to **Categories** — the checklist will be suggested automatically for tenders in those categories.

**Step 4:** Add requirements under the **Requirements** tab:

| Field | Description |
|-------|-------------|
| **Requirement** | Description (e.g. "Valid tax clearance certificate") |
| **Mandatory** | Is this a hard requirement? |
| **Requires Document** | Does the user need to upload supporting evidence? |
| **Details** | Additional context |
| **Guidance** | Help text for the user completing the checklist |

### 6.2 Applying a checklist to a tender

**Step 1:** Open a tender and click **Action → Apply Compliance Checklist** (or the Compliance smart button if available).

**Step 2:** Select the appropriate checklist from the list.

**Step 3:** The system creates a **Compliance Result** with one line per requirement, each pre-populated from the checklist template.

### 6.3 Completing compliance checks

**Step 1:** Open the compliance result from the tender form or under **Compliance → Results**.

**Step 2:** Work through each line:

- Check **Compliant** when the requirement is met
- Add **Notes** to document evidence
- Upload **Supporting Documents** (attachments)

**Step 3:** The **Compliance %** updates in real-time as you check items off.

> **⚠️ Warning:** Aim for **100% compliance** before submission. Most public-sector tenders disqualify non-compliant bids outright.

### 6.4 Reusing checklists

Checklists linked to categories are suggested automatically. You can apply multiple checklists to the same tender if different sections of the RFP have different requirements.

---

## 7. AI Document Analysis

Use AI to extract insights from tender documents — saving hours of manual reading.

### 7.1 Configuring the AI provider

**Step 1:** Go to **Settings → Technical → System Parameters**.

**Step 2:** Add or edit `zakheni_tender.ai_api_key` with your API key.

**Step 3 (optional):** For custom endpoints, add `zakheni_tender.ai_custom_endpoint`.

Supported providers:
- **OpenAI** (default) — uses `gpt-4o-mini`
- **Anthropic** — uses `claude-3-haiku-20240307`
- **Custom API** — any endpoint that accepts `{"prompt": "..."}` and returns text

### 7.2 Running AI analysis

**Step 1:** Open the tender and upload the RFP/document under the **Documents** tab.

**Step 2:** Click the **AI Analysis** stat button in the button box.

**Step 3:** In the analysis popup:
- Select the **Source Document** (the document you uploaded)
- Choose the **AI Provider**
- Click **Run Analysis**

**Step 4:** The AI processes the document and returns structured results:

| Output | Description |
|--------|-------------|
| **Executive Summary** | 2–3 sentence overview |
| **Requirements** | Key requirements extracted from the document |
| **Key Deadlines** | Critical dates found |
| **Compliance Items** | Compliance requirements mentioned |
| **Risk Factors** | Potential risks identified |
| **Bid Recommendation** | Recommended / Not Recommended / Needs Review |
| **Confidence Score** | How confident the AI is in its analysis |

### 7.3 Reviewing results

The results are displayed in a tabbed notebook:
- Summary
- Requirements
- Deadlines
- Compliance Items
- Risk Factors
- Raw Response (full JSON for power users)

> **💡 Tip:** Always review AI output before relying on it. The AI may miss context-specific nuances or local regulations.

### 7.4 Re-analysis

If you add new documents or want to re-run with a different provider, create a new AI analysis record. Previous analyses remain available for comparison.

---

## 8. Tender Feeds & Discovery

The module automatically fetches open tenders from **eTenders.gov.za** (South Africa's official tender portal) using their free OCDS API.

### 8.1 How feeds work

- **Cron job:** Runs daily and imports new tenders from the OCDS API
- **Feed record:** Each imported tender becomes a `tender.feed` record
- **Status flow:** `New → Matched → Imported → Archived`

### 8.2 Viewing the tender feed

Go to **Tenders → Tender Feed**. You see imported tenders in Kanban and List views with:

- Tender name and reference
- Issuer name
- OCDS category
- Submission deadline
- Estimated value
- Match status and score

### 8.3 Keyword search on eTenders

**Step 1:** Go to **Tenders → Tender Feed** and click **Search eTenders by Keyword** (or via Configuration → Preconfigured Keywords → Run Now for persistent queries).

**Step 2:** Enter comma-separated keywords (e.g. `IT, Cisco, Networking, Johannesburg`).

**Step 3:** Set the look-back period (default 7 days).

**Step 4:** Click **Search & Fetch**.

The system fetches fresh data from the OCDS API and filters results matching your keywords.

### 8.4 Importing a feed as a tender

**Step 1:** Open any feed record from the Kanban or list.

**Step 2:** Click **Import to Tender**.

The system:
1. Creates a new `tender.tender` with all relevant fields copied
2. Creates or matches the issuer as a `res.partner`
3. Sets the feed status to **Imported**
4. Opens the new tender form for further editing

### 8.5 Preconfigured Keywords (persistent searches)

Under **Configuration → Preconfigured Keywords**, you can set up keyword configs that run automatically on the daily cron:

- **Name** — label for the config
- **Keywords** — comma-separated search terms
- **Min Days to Deadline** — only match tenders with enough prep time
- **Link to Company Profile** — optional; used for auto-matching

Click **Run Now** to trigger an immediate search.

---

## 9. Company Profiles & Auto-Matching

Configure your organisation's capabilities, then let the system automatically find tenders that match.

### 9.1 Creating a company profile

**Step 1:** Go to **Tenders → Matching → Company Profiles** and click **New**.

**Step 2:** Select your company (linked to `res.partner`).

**Step 3:** Configure:

| Section | Fields |
|---------|--------|
| **Company Info** | Sector, B-BBEE Level |
| **Services** | Service Categories (linked to OCDS keywords), Regions |
| **Capabilities** | Min/Max project value, Employee count, Years in business, Annual turnover |
| **Description** | Free-text describing your capabilities and differentiators (used for NLP embedding) |
| **Search Preferences** | Min Days to Deadline (default 14) |

### 9.2 Service Categories

Configured under **Configuration → Service Categories**, these link your business services to OCDS search keywords:

| Field | Description |
|-------|-------------|
| Name | e.g. "IT Infrastructure" |
| Code | Optional short code |
| Parent Category | Hierarchical nesting |
| OCDS Keywords | Comma-separated keywords matched against the eTenders OCDS API (e.g. "Network, Cisco, Router, Switch") |

Click **Search on eTenders** from a service category to find matching tenders immediately.

### 9.3 Running auto-matching

**Step 1:** Open a company profile and click **Find Matching Tenders**.

**Step 2:** The system:
1. Fetches fresh tenders from eTenders
2. Filters by your service category keywords and preconfigured keyword configs
3. Computes **NLP similarity** between your profile description and each tender
4. Creates **Tender Match** records with similarity scores

**Step 3:** Review matches under **Matching → Matches**.

### 9.4 Understanding match scores

| Score | Category | Action |
|-------|----------|--------|
| > 50% | High match | Review immediately; strong alignment |
| 30–50% | Medium match | Worth a quick review |
| < 30% | Low match | Probably not relevant |

### 9.5 Match workflow

Each match goes through states:

1. **Pending** — newly matched, awaiting review
2. **Reviewed** — you've looked at it
3. **Interested** — you want to bid; auto-imports as a tender
4. **Not Interested** — decline

> **💡 Tip:** When you mark a match as **Interested**, the system automatically imports the feed as a tender — saving you a manual step.

### 9.6 Automated cron matching

The system runs two automated jobs:
- **Every 12 hours:** Re-computes NLP matches for all active profiles against new feeds
- **Every 24 hours:** Fetches fresh tenders from the OCDS API and runs keyword + NLP matching

> **💡 Tip:** Ensure `sentence-transformers` is installed on your server for NLP matching. Otherwise, matching falls back to keyword-only filtering.

---

## 10. Portal Access for Bidders

External users (bidders, issuers, team members) can view tender information and upload documents through the Odoo customer portal.

### 10.1 What portal users see

Portal users with access to a tender (via `message_partner_ids` or as a linked contact of the issuer) can:

- View a list of **My Tenders** at `/my/tenders`
- Sort by deadline, name, value, or date
- See tender status (badge), stage, value, and deadline
- Open a tender detail page showing:
  - Full tender information
  - Scope of Work
  - Current stage, value, deadline, win probability
  - Status badges (Won / Lost / In Progress)

### 10.2 Uploading documents via portal

**Step 1:** Log into the portal and navigate to **My Tenders → [Tender Name]**.

**Step 2:** In the right sidebar, under **Upload Document**:
1. Click **Choose File** to select a file (or multiple files)
2. Optionally enter a **Resource Name** (e.g. "Project Manager CV", "Company Profile")
3. Click **Upload**

**Step 3:** The document appears in the **Documents** section, grouped by resource name.

### 10.3 Portal access setup

To give a contact portal access to a tender:
1. Add them to the tender's **message partners** (chatter followers) or
2. Set them as the issuer contact (res.partner child relation)

The portal automatically counts and displays all accessible tenders on the portal home page.

> **💡 Tip:** Encourage bidders to upload documents with meaningful resource names — this helps your compliance team organise submissions by category.

---

## 11. Dashboards & Reporting

### 11.1 Dashboard

Go to **Tenders → Dashboard** for a real-time overview:

| KPI | Description |
|-----|-------------|
| **Total Tenders** | All-time count |
| **Won** (with value) | Number won + total quoted value |
| **Lost** (with withdrawn) | Number lost + withdrawn count |
| **In Progress** (with overdue) | Active tenders + how many are past deadline |
| **Win Rate** | % of decided tenders that were won |
| **Average Tender Value** | Mean estimated value across all tenders |
| **Total Pipeline Value** | Sum of estimated values for all tenders |

Also shows:
- **Pipeline by Stage** — list view with win probability per stage
- **Win Rate** — prominent percentage with decided-tender context

### 11.2 Analysis views

Go to **Tenders → Analysis** for deeper exploration:

**Pivot view:**
- Rows: Responsible person
- Columns: Stage
- Measures: Tender Value, Quoted Amount, Probability, Duration Days

**Graph views:**
- Tender Value by Responsible (bar chart)
- Tenders by Stage (bar chart)
- Results by Value (pie chart)

### 11.3 Built-in reports on the tender list

The **Tenders** list view includes:
- **Graph** — tender value by responsible
- **Pivot** — cross-tab by user and stage
- **Calendar** — deadline timeline

### 11.4 Standard Odoo reporting

You can also:
- Use **Favorites → Add Custom Filter** to save frequent searches
- Export any list view to **Excel** or **CSV** for offline analysis
- Use the **Pivot** view with multiple dimensions for custom cross-tab analysis
- Create custom **Dashboard** dashboards with Odoo Studio (Enterprise only)

### 11.5 Alert-driven reporting

The system automatically creates alerts under **Settings → Technical → Scheduled Actions**:

| Cron Job | Frequency | What It Does |
|----------|-----------|--------------|
| Tender Deadline Alerts | Every 6 hours | Checks approaching and overdue deadlines; posts chatter messages |
| Tender Feed Matching | Every 12 hours | Runs NLP matching against all active profiles |
| Fetch eTenders OCDS | Every 24 hours | Imports new tenders and runs keyword matching |

> **💡 Tip:** Deadline alerts appear in the tender's chatter stream and notify the responsible user and team members.

---

## 12. Configuration & Administration

### 12.1 Stages (Pipeline)

Under **Configuration → Stages**, manage the lifecycle stages. See [Section 4.5](#45-configuring-stages).

### 12.2 Categories

Under **Configuration → Categories**, create tender categories (e.g. IT, Construction, Consulting). These are used for filtering, compliance checklist suggestions, and reporting.

### 12.3 Service Categories

Under **Configuration → Service Categories**, define the services your organisation offers. Each service category can have:
- **OCDS Search Keywords** — used by the auto-matching engine
- **Parent-child hierarchy** — for organisational structure

### 12.4 Preconfigured Keywords

Under **Configuration → Preconfigured Keywords**, set up persistent keyword searches that run automatically. See [Section 8.5](#85-preconfigured-keywords-persistent-searches).

### 12.5 Security & access rights

The module uses Odoo's standard access control. Available groups (configured in `ir.model.access.csv`):
- **User** — can view and manage tenders, feeds, and profiles
- **Administrator** — full configuration access

### 12.6 System parameters

Key system parameters (set via *Settings → Technical → System Parameters*):

| Key | Description |
|-----|-------------|
| `zakheni_tender.ai_api_key` | API key for AI analysis (OpenAI/Anthropic/Custom) |
| `zakheni_tender.ai_custom_endpoint` | Custom AI API endpoint URL |

---

## 13. FAQ & Troubleshooting

### Why aren't new tenders appearing in the feed?

- The OCDS cron runs **once daily**. Check *Settings → Technical → Scheduled Actions → Fetch Tenders from eTenders OCDS API* for the next run time.
- Click **Search eTenders by Keyword** to force an immediate fetch.

### The AI analysis returns an error

1. Verify your API key is set in `zakheni_tender.ai_api_key`
2. Check the **Raw Response** or **Error** tab for details
3. Ensure the document is not too large (limited to 50,000 characters)
4. Try switching providers (OpenAI vs Anthropic)

### NLP matching isn't finding any results

- Install `sentence-transformers` on the Odoo server: `pip install sentence-transformers`
- Add OCDS keywords to your **Service Categories**
- Update your **Company Profile** description with detailed capability information
- Click **Compute Embedding** on the profile, then **Find Matching Tenders**
- Check that the **Min Days to Deadline** isn't filtering out all results

### Portal users can't see a tender

- Ensure the user's portal contact is either:
  - A follower of the tender (added via the chatter)
  - A child contact of the tender's issuer

### Can I import historical tenders?

Yes — manually create them (Section 3.1). You can also set a custom date in the form fields.

### How do I customise the pipeline stages?

Go to **Configuration → Stages**. You can rename, reorder, add, or remove stages. Existing tenders retain their assigned stage.

### The compliance percent seems wrong

Compliance is calculated as: (completed items / total items) × 100. Items are "completed" only when **Compliant** is checked. Partial compliance is not counted.

### Can I have multiple company profiles?

Yes — one per company/entity. Each profile has its own service categories, keywords, and match history.

---

> **Document version:** 1.0  
> **Last updated:** July 2026  
> **Support:** For module support, contact Zakheni ICT at https://www.zakhenict.co.za
