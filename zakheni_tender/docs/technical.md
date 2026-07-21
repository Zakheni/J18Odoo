# Zakheni Tender Management — Technical Document

## 1. System Requirements

| Component | Requirement |
|-----------|-------------|
| Odoo Version | 18.0 |
| Python | 3.10+ (3.12 on current server) |
| PostgreSQL | 12+ |
| RAM | 4 GB+ (8 GB recommended for NLP) |

### Python Dependencies

Installed automatically or via pip:
```
requests              — HTTP client for OCDS API
sentence-transformers — NLP embeddings for semantic matching
numpy                 — Cosine similarity computation
```

Install matching dependencies:
```bash
pip install sentence-transformers numpy
```

## 2. Installation

### Via addons path
```bash
# Copy module to addons directory
cp -r zakheni_tender /odoo/custom-addons/

# Restart Odoo service
systemctl restart odoo

# Install module via CLI
odoo-bin -c odoo.conf -d odoo18 -i zakheni_tender --stop-after-init

# Or via Odoo UI: Apps → Remove "Apps" filter → Search "Zakheni Tender" → Install
```

### Upgrade
```bash
odoo-bin -c odoo.conf -d odoo18 -u zakheni_tender --stop-after-init
systemctl restart odoo
```

## 3. Module Structure

```
zakheni_tender/
├── __init__.py                    # Module loader
├── __manifest__.py                # Module manifest (v18.0.1.3.0)
├── controllers/
│   ├── __init__.py
│   └── portal.py                  # Customer portal routes
├── data/
│   ├── cron_data.xml              # Cron job definitions
│   └── stages.xml                 # Default pipeline stages (noupdate)
├── models/
│   ├── __init__.py                # Model registry (17 models)
│   ├── tender.py                  # Core tender model (tender.tender)
│   ├── tender_ai_analysis.py      # AI document analysis
│   ├── tender_alert.py            # Deadline alerts
│   ├── tender_analysis.py         # SQL analysis view
│   ├── tender_bid_no_bid.py       # Bid/No-Bid scoring
│   ├── tender_category.py         # Tender categories
│   ├── tender_company_profile.py  # Company profile + keyword matching
│   ├── tender_compliance.py       # Compliance checklists
│   ├── tender_dashboard.py        # Transient dashboard model
│   ├── tender_document.py         # Tender documents
│   ├── tender_document_resource.py# Document resource groups
│   ├── tender_feed.py             # Tender feed + OCDS API + keyword matching
│   ├── tender_feed_keyword_config.py    # Preconfigured keywords
│   ├── tender_feed_keyword_search.py    # Manual keyword search (transient)
│   ├── tender_feed_match.py       # Feed-to-profile matches
│   ├── tender_service_category.py # Service categories with OCDS keywords
│   └── tender_stage.py            # Pipeline stage definition
├── security/
│   └── ir.model.access.csv        # ACLs (user + system groups)
├── static/
│   ├── description/icon.png       # Module icon
│   └── src/scss/tender_dashboard.scss  # Dashboard styling
└── views/
    ├── menus.xml                  # Menu hierarchy
    ├── analysis_views.xml         # Pivot/Graph views
    ├── dashboard_views.xml        # Dashboard form
    ├── portal_templates.xml       # Portal QWeb templates
    ├── tender_ai_analysis_views.xml
    ├── tender_bid_no_bid_views.xml
    ├── tender_category_views.xml
    ├── tender_company_profile_views.xml
    ├── tender_compliance_views.xml
    ├── tender_feed_keyword_config_views.xml
    ├── tender_feed_keyword_search_views.xml
    ├── tender_feed_match_views.xml
    ├── tender_feed_views.xml
    ├── tender_service_category_views.xml
    ├── tender_stage_views.xml
    └── tender_views.xml
```

## 4. API Integration — eTenders OCDS

### Endpoint
```
GET https://ocds-api.etenders.gov.za/api/OCDSReleases
```

### Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| PageNumber | 1..N | Pagination |
| PageSize | 500 | Results per page |
| dateFrom | YYYY-MM-DD | Start date |
| dateTo | YYYY-MM-DD | End date |

### Authentication
None required (public API).

### Data Flow
```
Odoo Cron (daily)
  │
  ▼
cron_fetch_etenders(days_back=7)
  │
  ├─► GET /api/OCDSReleases?PageNumber=1&PageSize=500&dateFrom=...&dateTo=...
  │     │
  │     ▼
  │   Parse OCDS release — extract tender, buyer, period, value
  │     │
  │     ▼
  │   _import_ocds_release() — create tender.feed record
  │     │
  │     ▼
  │   _compute_embedding() — NLP vector from feed text
  │
  └─► Next page (loop until no links.next)
  │
  ▼
cron_fetch_keyword_tenders()
  │
  ├─► Get all active Company Profiles
  │     │
  │     ▼
  │   Collect keywords from:
  │     • Service Categories → ocds_keywords
  │     • Preconfigured Keywords → keywords (linked to profile)
  │     │
  │     ▼
  │   _search_feeds_by_keywords() — filter feeds by keyword match
  │     │
  │     ▼
  │   _match_against_profiles() — NLP cosine similarity >= 0.3
  │     │
  │     ▼
  │   Create tender.feed.match records
  │
  └─► Process standalone keyword configs (no profile link)
```

### OCDS Field Mapping
| OCDS Field | Odoo Field |
|------------|------------|
| release/ocid | external_id |
| tender/title | name |
| tender/description | description, description_text |
| tender/tenderPeriod/endDate | deadline_submission |
| tender/tenderPeriod/startDate | date_published |
| tender/value/amount | tender_value |
| buyer/name | issuer_name |
| tender/province | province |
| tender/category | ocds_category |
| tender/id | tender_number |

## 5. NLP Matching Pipeline

### Models Used
- **sentence-transformers/all-MiniLM-L6-v2** (384-dim embeddings)
- Lightweight (80MB), runs on CPU

### Matching Process
```
Feed Text                          Profile Text
    │                                    │
    ▼                                    ▼
_encode(feed_text)                 _encode(profile_text)
    │                                    │
    ▼                                    ▼
feed_vec (384 floats)              profile_vec (384 floats)
    │                                    │
    └──────────► _cosine_similarity() ◄──┘
                        │
                        ▼
                score >= 0.3? ──► create tender.feed.match
```

### Cosine Similarity Threshold
- **≥ 0.3**: Match created
- Higher scores = stronger semantic match
- Uses `numpy.linalg.norm` for vector normalization

## 6. Pipeline Stages (Default)

| Stage | Sequence | Probability | Fold |
|-------|----------|-------------|------|
| Identified | 10 | 5% | No |
| Reviewing | 20 | 15% | No |
| Preparing | 30 | 30% | No |
| Submitted | 40 | 50% | No |
| Under Evaluation | 50 | 60% | No |
| Won | 60 | 100% | Yes |
| Lost | 70 | 0% | Yes |

Stages are defined in `data/stages.xml` with `noupdate="1"` — custom stages survive upgrades.

## 7. Access Rights

All models use the standard two-tier pattern:
- **base.group_user** (Employee): Read access + create/edit their own records
- **base.group_system** (Administration): Full CRUD

**Exception**: `tender.dashboard` and `tender.analysis` are read-only for regular users.

### Model Access Details
| Model | User Read | User Write | User Create | User Unlink |
|-------|-----------|------------|-------------|-------------|
| tender.stage | Yes | No | No | No |
| tender.tender | Yes | Yes | Yes | No |
| tender.dashboard | Yes | No | No | No |
| tender.analysis | Yes | No | No | No |
| tender.document | Yes | Yes | Yes | Yes |
| tender.feed | Yes | No | No | No |
| tender.feed.match | Yes | No | No | No |
| tender.feed.keyword.config | Yes | Yes | Yes | Yes |
| tender.company.profile | Yes | Yes | Yes | No |
| All others | Yes | Depends | Depends | Depends |

## 8. Cron Jobs Reference

| Technical Name | Method | Interval | Active |
|----------------|--------|----------|--------|
| cron_tender_deadline_alerts | tender.alert._cron_check_deadlines() | 6 hours | Yes |
| cron_tender_feed_match | tender.feed.match.cron_compute_matches() | 12 hours | Yes |
| cron_tender_fetch_tenders_sa | tender.feed.cron_fetch_tenders_sa() | 24 hours | No (paid API) |
| cron_tender_fetch_etenders | tender.feed.cron_fetch_etenders() + cron_fetch_keyword_tenders() | 24 hours | Yes |

## 9. Performance Considerations

- **NLP embedding** runs synchronously per feed record — batch processing is recommended
- **OCDS API fetch** paginates 500 records per page — respects API rate limits
- **Dashboard** uses TransientModel — data is fresh on each access, no table bloat
- **SQL view** `tender.analysis` — materialized via `CREATE OR REPLACE VIEW`

## 10. Known Warnings (Non-Critical)

```
Field tender.feed.match.state: unknown parameter 'tracking'
Two fields (feed_ids, feed_count) of tender.feed.keyword.config()
  have the same label: Matched Feeds.
Two fields (name, requirement_id) of tender.compliance.result.line()
  have the same label: Requirement.
```

These are cosmetic label duplicates and do not affect functionality.
