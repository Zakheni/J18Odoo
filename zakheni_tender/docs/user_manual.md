# Zakheni Tender Management — User Manual

## Table of Contents
1. [Getting Started](#1-getting-started)
2. [Pipeline Management](#2-pipeline-management)
3. [Company Profile Setup](#3-company-profile-setup)
4. [Service Categories](#4-service-categories)
5. [Preconfigured Keywords](#5-preconfigured-keywords)
6. [Tender Feed & Matching](#6-tender-feed--matching)
7. [Bid/No-Bid Analysis](#7-bidno-bid-analysis)
8. [Compliance Management](#8-compliance-management)
9. [AI Document Analysis](#9-ai-document-analysis)
10. [Dashboard & Analysis](#10-dashboard--analysis)
11. [Customer Portal](#11-customer-portal)
12. [Alerts](#12-alerts)
13. [Workflows](#13-workflows)

---

## 1. Getting Started

### First-Time Setup Checklist

1. **Install the module** — Apps → Remove "Apps" filter → Search "Zakheni Tender" → Install
2. **Configure pipeline stages** — Tenders → Configuration → Stages (edit as needed)
3. **Set up your Company Profile** — Tenders → Matching → Company Profiles
4. **Add Service Categories** — Tenders → Configuration → Service Categories
5. **Add OCDS keywords** to each Service Category
6. **(Optional) Preconfigure Keywords** — Tenders → Configuration → Preconfigured Keywords
7. **The cron will fetch tenders automatically**, or click "Find Matching Tenders" on your profile

### Navigating the Module

```
Tenders
├── Tenders                  ── Pipeline (Kanban by stage)
├── Dashboard                ── KPI overview
├── Tender Feed              ── Imported tenders from eTenders
├── Analysis                 ── Pivot and graph reports
├── Bid/No-Bid Analysis      ── Go/no-go decisions
├── Compliance               ── Checklists and results
│   ├── Checklists
│   └── Results
├── Matching                 ── Profile-based matching
│   ├── Company Profiles
│   └── Matches
└── Configuration
    ├── Stages
    ├── Categories
    ├── Service Categories
    └── Preconfigured Keywords
```

---

## 2. Pipeline Management

### Viewing the Pipeline

Click **Tenders → Tenders**. The default view is a Kanban pipeline grouped by stage:

```
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ Identified │  │ Reviewing  │  │ Preparing  │  │ Submitted  │
│            │  │            │  │            │  │            │
│  ├─ Tender │  │  ├─ Tender │  │  ├─ Tender │  │  ├─ Tender │
│  ├─ Tender │  │            │  │            │  │  ├─ Tender │
│            │  │            │  │            │  │            │
├────────────┤  ├────────────┤  ├────────────┤  ├────────────┤
│ Under      │  │    Won     │  │    Lost    │  │            │
│ Evaluation │  │  (folded)  │  │  (folded)  │  │            │
│            │  │            │  │            │  │            │
│  ├─ Tender │  │            │  │            │  │            │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

- **Drag and drop** tenders between stages to update their stage
- **Won** and **Lost** stages are folded by default (hidden until you scroll)
- Click any card to open the tender form

### Moving a Tender Through Stages

1. **Identified** → A new opportunity is identified
2. **Reviewing** → Evaluate RFP documents, decide whether to bid
3. **Preparing** → Drafting proposal, gathering documents
4. **Submitted** → Bid submitted before deadline
5. **Under Evaluation** → Issuer evaluating bids
6. **Won** or **Lost** → Final outcome

To mark Won/Lost:
- Open the tender form
- Click **"Mark Won"** or **"Mark Lost"** in the header
- The stage and result are updated automatically

### Editing Stages

Tenders → Configuration → Stages
- Add, rename, or reorder stages
- Set win probability percentages
- Mark stages as Won or Lost stages
- **Fold** hides completed stages from the default Kanban view

### List View

Switch to list view (icon top-right) for a sortable table of all tenders:
- Columns: Tender Ref, Name, Issuer, Stage, Responsible, Deadline, Value, Probability, Result
- Use filters: Stage, Responsible, Result
- Group by: Stage, Responsible, Result

---

## 3. Company Profile Setup

The company profile drives automated tender matching. Set it up once and the system will find relevant tenders.

### Creating a Profile

1. Go to **Tenders → Matching → Company Profiles**
2. Click **Create**
3. Fill in:

| Field | Description | Example |
|-------|-------------|---------|
| Company | Your company (auto-filled) | Zakheni ICT (Pty) Ltd |
| Primary Sector | Your main industry | Information Technology |
| B-BBEE Level | Your BBBEE level | Level 1 |
| Service Categories | What services you offer | Software Development, IT Consulting |
| Service Regions | Which provinces you operate in | Gauteng, Western Cape |
| Min/Max Project Value | Project size range | R100,000 – R10,000,000 |
| Company Capabilities | Describe expertise (used for AI matching) | "We specialise in enterprise software..." |
| Min Days to Deadline | Minimum days until deadline for matched tenders | 14 |

4. Click **Save**
5. Click **Compute Embedding** to generate the NLP vector for matching

> **Tip:** The **Min Days to Deadline** field (default: 14) ensures you only see tenders
> with enough time to evaluate documents and prepare a quality submission. Tenders
> closing sooner are still available in the full Tender Feed but won't appear in
> profile-based matching results.

### Finding Matching Tenders

On the profile form, click **"Find Matching Tenders"**:
1. Fetches latest tenders from eTenders (7 days back)
2. Filters by keywords from your Service Categories and Preconfigured Keywords
3. Filters out tenders closing before **Min Days to Deadline** (default 14 days)
4. Runs NLP semantic matching
5. Opens matching tenders list

Repeat this whenever you want to refresh results.

---

## 4. Service Categories

Service Categories define what your company does. Their OCDS keywords are used to search for relevant tenders.

### Creating a Service Category

1. Go to **Tenders → Configuration → Service Categories**
2. Click **Create**
3. Set **Name** (e.g., "IT Infrastructure")
4. Set **OCDS Search Keywords** (comma-separated, these are matched against tender titles and categories)

### OCDS Keywords Examples

| Service Category | OCDS Keywords |
|-----------------|---------------|
| Software Development | software, development, application, system, platform |
| IT Infrastructure | infrastructure, network, hardware, server, firewall |
| Consulting | consulting, advisory, feasibility, assessment |
| Construction | construction, building, renovation, infrastructure |
| Security | security, guard, surveillance, access control |

### How Keywords Are Used

When matching runs:
1. All keywords from **all active Service Categories** on your profile are collected
2. They are matched against `ocds_category`, `name`, and `description_text` of imported feeds
3. A match is found if ANY keyword appears in any of these fields

---

## 5. Preconfigured Keywords

Add extra keywords beyond what's in your Service Categories.

### Adding Keywords to a Profile

**From the Profile form:**
1. Open your Company Profile
2. Go to the **"Preconfigured Keywords"** tab
3. Click **Add a line**
4. Enter Name (e.g., "Solar Projects") and Keywords (e.g., "solar, photovoltaic, renewable")
5. The **Active** checkbox must be checked

**From Configuration (standalone):**
1. Go to **Tenders → Configuration → Preconfigured Keywords**
2. Click **Create**
3. Optionally link to a **Company Profile** (if left empty, it runs as standalone)
4. Enter keywords (comma-separated)

### Run Now

On a keyword config, click **"Run Now"** to immediately:
1. Fetch latest eTenders
2. Search for matches
3. Link matched feeds
4. Update the feed count

---

## 6. Tender Feed & Matching

The Tender Feed shows all imported tenders from eTenders.gov.za.

### Viewing the Feed

**Tenders → Tender Feed**

Columns: Tender Name, Reference, Issuer, Source, OCDS Category, Deadline, Value, Status, Match Score, Matches

Filters available:
- Status: New, Matched
- Imported: Yes/No
- Group by Status or Source

### Feed Statuses

| Status | Meaning |
|--------|---------|
| **New** | Imported from API, not yet matched |
| **Matched** | NLP match found against a company profile |
| **Imported** | Converted to a tender.tender record |
| **Archived** | No longer relevant |

### Feed Actions

On a feed record:
- **Run Matching** — Run NLP matching against all active profiles
- **Import to Tender** — Create a tender.tender record from this feed
- **View Imported Tender** — Open the linked tender (if imported)

### Matching Workflow

**Automated (cron):** Runs every 12 hours automatically
1. Fetches new eTenders
2. Collects keywords from profiles + configs
3. Filters feeds by keyword match
4. Runs NLP cosine similarity (threshold: 0.3)
5. Creates match records

**Deadline filter:** Both automatic and manual matching exclude tenders that close
before the profile's **Min Days to Deadline** setting. This gives you 2–3 weeks
(default: 14 days) to evaluate and prepare submissions.

**Manual:** Click "Find Matching Tenders" on a Company Profile, or "Run Matching" on a feed.

### Match Statuses

| Status | Action |
|--------|--------|
| Pending | New match, awaiting review |
| Reviewed | You've looked at it |
| Interested | You want to bid — imports to Tenders automatically |
| Not Interested | Not relevant |

---

## 7. Bid/No-Bid Analysis

A structured framework to decide whether to bid on a tender.

### Creating a Bid/No-Bid Analysis

1. Open a tender
2. Click the **Bid/No-Bid** stat button (or Actions → Bid/No-Bid)
3. Default criteria are auto-created with weights

### Scoring Criteria

| Category | Criteria | Weight |
|----------|----------|--------|
| Strategic | Alignment with business strategy | 3.0 |
| Strategic | Market presence & growth | 2.0 |
| Financial | Estimated profitability | 4.0 |
| Financial | Bid cost vs potential return | 3.0 |
| Capacity | Available team capacity | 3.0 |
| Capacity | Required skills available | 3.0 |
| Competitive | Position & differentiators | 2.0 |
| Competitive | Past performance with issuer | 2.0 |
| Risk | Contractual risk | 3.0 |
| Risk | Project delivery risk | 2.0 |
| Compliance | Eligibility & requirements | 4.0 |
| Compliance | B-BBEE scoring level | 3.0 |

### How to Score

For each criterion:
- Rate from **0 (poor)** to **10 (excellent)**
- The weighted score = weight × score ÷ 10
- Total score = sum of weighted scores ÷ sum of weights × 100

### Recommendation

| Score | Recommendation |
|-------|---------------|
| ≥ 70% | **Bid** |
| 40–69% | **No-Bid** (review before deciding) |
| < 40% | **No-Bid** |

---

## 8. Compliance Management

### Creating a Checklist

1. **Tenders → Compliance → Checklists**
2. Click **Create**
3. Add line items with mandatory flags

Example checklist for South African tenders:
```
Checklist: Standard Tender Requirements
├── Valid Tax Clearance Certificate (Mandatory)
├── BBBEE Affidavit/Certificate (Mandatory)
├── CIDB Registration (if applicable)
├── CSD Report
├── Letter of Good Standing (COIDA)
├── Company Registration Documents
├── Signed SBD Forms
└── Bank Confirmation Letter
```

### Applying a Checklist to a Tender

1. Open a tender
2. Click the **Compliance** stat button (or Actions → Apply Compliance Checklist)
3. Select a checklist
4. Mark each item as satisfied or not
5. The compliance result is linked to the tender

---

## 9. AI Document Analysis

Upload tender documents for AI-powered analysis.

### Running Analysis

1. Open a tender
2. Click the **AI Analysis** stat button
3. Upload a document (PDF, DOCX, etc.)
4. Click **Analyze**
5. Results appear in the analysis text field

### Requirements

- AI model support requires configuration
- Document is sent to the configured AI service for analysis

---

## 10. Dashboard & Analysis

### Dashboard

**Tenders → Dashboard**

Shows:
- **Total Tenders** — All time
- **Won** — Count and total value
- **Lost** — Count and withdrawn count
- **In Progress** — Active tenders (overdue highlighted)
- **Win Rate** — Percentage of decided tenders won
- **Pipeline by Stage** — Stages with probability percentages
- **Average Tender Value**
- **Total Pipeline Value**

Data refreshes each time you open the dashboard.

### Analysis

**Tenders → Analysis**

Pivot and graph views for data analysis:
- Group by Responsible, Stage, Issuer, Result
- Measures: Tender Value, Quoted Amount, Count
- Graph types: Bar, Line, Pie

---

## 11. Customer Portal

External users can view and interact with tenders through the portal.

### Portal Access

Route: `https://your-odoo-instance/my/tenders`

Customers see:
- Tenders they are listed as Issuer or message partner
- Deadline, value, and stage information
- Document upload capability

### Document Upload

Portal users can:
1. View tender details
2. Create document resources (e.g., "Proposal", "Financials")
3. Upload files to resources
4. Download previously uploaded documents

---

## 12. Alerts

### Deadline Alerts

The system automatically checks every 6 hours:
- Approaching submission deadlines
- Expired bid bonds
- Validity period endings

Alerts appear in the Odoo notification system and on the tender record.

### Viewing Alerts

Alerts are stored as `tender.alert` records linked to each tender.

---

## 13. Workflows

### Workflow A: From Feed to Won Tender

```
1. System imports tender from eTenders (daily cron)
       │
2. Keyword matching finds the tender (profile-based)
       │
3. NLP matching creates match record (score ≥ 0.3)
       │
4. User reviews match → marks as "Interested"
       │
5. Automatically imports to Tenders as tender.tender
       │
6. User completes Bid/No-Bid analysis
       │
7. Add documents, assign team, track compliance
       │
8. Submit bid before deadline
       │
9. Move to Under Evaluation → Won/Lost
       │
10. Record result, update pipeline
```

### Workflow B: Manual Tender Entry

```
1. Tenders → Tenders → Create
2. Enter name, reference, issuer
3. Set stage to "Identified"
4. Add description, deadlines, financials
5. Attach documents
6. Move through pipeline stages manually
```

### Workflow C: Compliance-First

```
1. Create compliance checklists (one-time setup)
2. When preparing a bid:
   a. Open tender
   b. Actions → Apply Compliance Checklist
   c. Select checklist
   d. Mark items as satisfied
   e. Review result
```

### Workflow D: Setup for New Company

```
1. → Company Profile → Create
2. → Service Categories → Create (add OCDS keywords)
3. → Profile → Add Service Categories
4. → Profile → Compute Embedding
5. → Profile → Find Matching Tenders
6. Review matches in Tender Feed
```

---

## Appendix: Quick Reference

### Keyboard Shortcuts
- **Ctrl+Enter** — Save and close current record
- **Ctrl+S** — Save
- **Ctrl+Shift+X** — Discard changes

### Common Fields Glossary

| Field | Model | Purpose |
|-------|-------|---------|
| Tender Reference | tender.tender | Issuer's reference number |
| Stage | tender.tender | Current pipeline stage |
| Probability | tender.tender | Win probability (0-100%) |
| Tender Value | tender.tender | Issuer's estimated value |
| Quoted Amount | tender.tender | Our bid amount |
| Bid Bond | tender.tender | Guarantee amount + expiry + bank |
| Deadline Submission | tender.tender | Bid closing date/time |
| Result | tender.tender | Won/Lost/Withdrawn/Cancelled |
| Similarity Score | tender.feed.match | NLP match strength (0.0-1.0) |
| OCDS Keywords | tender.service.category | Search terms for eTenders |
| Embedding | tender.company.profile | NLP vector of company capabilities |
