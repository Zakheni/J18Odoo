# Zakheni Tender Management — Design Document

## 1. Overview

Zakheni Tender Management is an Odoo 18 module for end-to-end tender lifecycle management. It covers opportunity identification from public feeds through bid preparation, submission, evaluation, and outcome tracking.

### Core Capabilities
- **Tender Pipeline** — Kanban pipeline grouped by stage (Identified → Reviewing → Preparing → Submitted → Under Evaluation → Won/Lost)
- **Automated Feed Import** — Fetches tenders daily from the South African eTenders OCDS API
- **Profile-Based Matching** — NLP semantic matching between company profiles and tender feeds
- **Bid/No-Bid Analysis** — Weighted scoring framework for go/no-go decisions
- **Compliance Management** — Checklists, certificates, and results per tender
- **AI Document Analysis** — Upload documents for AI-powered analysis
- **Customer Portal** — External users can view tenders and upload documents
- **Deadline Alerts** — Automatic notifications for approaching deadlines

## 2. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Odoo 18 Server                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              zakheni_tender Module                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌───────────────────┐  │  │
│  │  │  Models   │  │  Views   │  │   Controllers     │  │  │
│  │  │  (20)     │  │  (16)    │  │   Portal (1)      │  │  │
│  │  └────┬─────┘  └──────────┘  └───────────────────┘  │  │
│  │       │                                              │  │
│  │  ┌────▼─────┐  ┌──────────┐  ┌───────────────────┐  │  │
│  │  │  Data    │  │ Security │  │   Assets/SCSS      │  │  │
│  │  │  (2)     │  │  (1)     │  │   (1)              │  │  │
│  │  └──────────┘  └──────────┘  └───────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              External Integrations                    │  │
│  │  eTenders OCDS API ──► Daily cron fetch              │  │
│  │  sentence-transformers ──► NLP matching               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 3. Data Model

### Core Tender Models

```
tender.stage
├── name, sequence, probability
├── fold (folded in kanban)
├── is_won, is_lost
└── description

tender.tender (inherits mail.thread, mail.activity.mixin)
├── name, tender_number, description
├── stage_id ───────────────► tender.stage
├── issuer_id ──────────────► res.partner
├── category_id ────────────► tender.tender.category
├── user_id ────────────────► res.users
├── team_ids ───────────────► res.users (M2M)
├── competitor_ids ─────────► res.partner (M2M)
├── document_ids ───────────► tender.document (O2M)
├── resource_ids ───────────► tender.document.resource (O2M)
├── bid_no_bid_id ──────────► tender.bid.no.bid
├── ai_analysis_ids ────────► tender.ai.analysis (O2M)
├── compliance_result_ids ──► tender.compliance.result (O2M)
├── Dates: deadline_submission, date_published, date_submitted, etc.
├── Financial: tender_value, quoted_amount, bid_bond_amount, etc.
└── Result: won/lost/withdrawn/cancelled, result_date, lost_reason

tender.document
├── name, datas (binary), file_size
├── tender_id ──────────────► tender.tender
├── resource_id ────────────► tender.document.resource
├── uploaded_by ────────────► res.users
└── uploaded_date

tender.document.resource
├── name, sequence, description
├── tender_id ──────────────► tender.tender
└── document_ids ───────────► tender.document (O2M)
```

### Tender Category

```
tender.tender.category
├── name, code, description
└── active
```

### Bid/No-Bid Analysis

```
tender.bid.no.bid
├── tender_id ──────────────► tender.tender
├── recommendation (bid/no-bid/pending)
├── score_percent
├── total_weight, total_score
└── line_ids ───────────────► tender.bid.no.bid.line (O2M)

tender.bid.no.bid.line
├── parent_id ──────────────► tender.bid.no.bid
├── category (strategic/financial/capacity/competitive/risk/compliance)
├── name
├── weight (1.0–5.0)
├── score (0–10)
└── notes
```

### Compliance

```
tender.compliance.checklist
├── name, active
└── line_ids ───────────────► tender.compliance.checklist.line (O2M)

tender.compliance.checklist.line
├── checklist_id ───────────► tender.compliance.checklist
├── name, mandatory
└── sequence

tender.compliance.result
├── tender_id ──────────────► tender.tender
├── checklist_id ───────────► tender.compliance.checklist
├── status (pass/fail/pending)
└── line_ids ───────────────► tender.compliance.result.line (O2M)

tender.compliance.result.line
├── result_id ──────────────► tender.compliance.result
├── requirement_id ─────────► tender.compliance.checklist.line
├── satisfied
└── notes
```

### AI Analysis

```
tender.ai.analysis
├── tender_id ──────────────► tender.tender
├── document_name, document_data (binary)
├── analysis_result (text)
├── model_used
├── analysis_date
└── status (pending/done/failed)
```

### Tender Feed & Matching

```
tender.feed
├── name, external_id, source (etender/tenders_sa/manual)
├── tender_number, issuer_name
├── issuer_id ──────────────► res.partner
├── category_id ────────────► tender.tender.category
├── description, description_text
├── deadline_submission, date_published
├── province, ocds_category
├── tender_value
├── status (new/matched/imported/archived)
├── url, raw_data
├── embedding (NLP vector), embedding_date
├── match_ids ──────────────► tender.feed.match (O2M)
├── imported_tender_id ─────► tender.tender
└── keyword_config_ids ─────► tender.feed.keyword.config (M2M)

tender.feed.match
├── feed_id ────────────────► tender.feed
├── company_profile_id ─────► tender.company.profile
├── partner_id (related)
├── similarity_score (0.0–1.0)
├── state (pending/reviewed/interested/not_interested)
└── match_date, notes

tender.feed.keyword.config
├── name, keywords (comma-separated)
├── profile_id ─────────────► tender.company.profile
├── active, last_fetch_date
├── feed_ids ───────────────► tender.feed (M2M)
└── feed_count (computed)

tender.feed.keyword.search (transient)
├── keywords, days_back
└── action_fetch()
```

### Company Profile

```
tender.company.profile
├── partner_id ─────────────► res.partner
├── sector, bee_level
├── service_category_ids ───► tender.service.category (M2M)
├── region_ids ─────────────► res.country.state (M2M)
├── min/max_project_value
├── employee_count, years_in_business, annual_turnover
├── description (capabilities)
├── embedding, embedding_date
├── match_ids ──────────────► tender.feed.match (O2M)
├── keyword_config_ids ─────► tender.feed.keyword.config (O2M)
└── match_count (computed)
```

### Service Category

```
tender.service.category
├── name, code, description
├── active
├── parent_id ──────────────► tender.service.category
├── child_ids (O2M)
└── ocds_keywords (comma-separated for OCDS API matching)
```

### Alerts

```
tender.alert
├── tender_id ──────────────► tender.tender
├── alert_type (deadline/bid_bond/validity/custom)
├── title, message
├── alert_date, reminded
├── state (draft/sent/done)
└── user_id ────────────────► res.users
```

### Analysis View (SQL)

```
tender.analysis (SQL view — _auto = False)
├── date, tender_id, user_id, stage_id
├── issuer_id, company_id, result
├── tender_value, quoted_amount, probability
├── duration_days, is_won, is_lost
└── currency_id
```

## 4. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Kanban pipeline as default view** | Provides visual stage-based workflow like Odoo CRM |
| **TransientModel for dashboard** | Compute on demand; no stale data stored in DB |
| **sentence-transformers for matching** | Semantic NLP matching vs. simple keyword — catches contextually relevant tenders |
| **eTenders OCDS API (free)** | No API key required, standard OCDS format, South African government tenders |
| **Profile-based feed search** | Keywords auto-derived from service categories + configs — no manual typing |
| **noupdate data files** | Pipeline stages and cron jobs survive module upgrades |
| **Mail integration** | Tender changes tracked via Odoo messaging, portal customers get updates |

## 5. Cron Jobs

| Cron | Interval | Function |
|------|----------|----------|
| Tender Deadline Alerts | Every 6 hours | Checks for approaching/passed deadlines |
| Tender Feed Matching | Every 12 hours | Runs NLP matching on unmatched feeds |
| Fetch eTenders + Keywords | Every 24 hours | Fetches OCDS data, runs profile-based keyword search + matching |

## 6. Customer Portal

Routes: `/my/tenders`, `/my/tender/<id>`, `/my/tender/<id>/upload`
- Authenticated portal users see tenders where they are the issuer or message partner
- Upload documents to tenders via portal
- Document resources group uploaded files by category

## 7. Security

All models use two-tier access:
- **base.group_user** — Read/create on own data, write/limited unlink
- **base.group_system** — Full CRUD (administration)
