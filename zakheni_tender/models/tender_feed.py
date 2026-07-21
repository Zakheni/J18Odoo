import logging
import json
from datetime import datetime, timedelta
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class TenderFeed(models.Model):
    _name = 'tender.feed'
    _description = 'Tender Feed'
    _inherit = ['mail.thread']
    _order = 'deadline_submission, id desc'

    name = fields.Char(string='Tender Name', required=True, tracking=True)
    external_id = fields.Char(string='External ID', help='ID from the external source')
    source = fields.Selection([
        ('etender', 'eTender.gov.za (OCDS)'),
        ('tenders_sa', 'Tenders-SA (paid)'),
        ('manual', 'Manual Entry'),
    ], string='Source', default='etender', tracking=True)

    tender_number = fields.Char(string='Tender Reference')
    issuer_name = fields.Char(string='Issuer')
    issuer_id = fields.Many2one('res.partner', string='Issuer (Matched)')
    category_id = fields.Many2one('tender.tender.category', string='Category')

    description = fields.Html(string='Description')
    description_text = fields.Text(string='Plain Text Description',
                                   help='Plain text version for embedding computation')

    deadline_submission = fields.Datetime(string='Submission Deadline', tracking=True)
    date_published = fields.Date(string='Publication Date')
    site_visit_date = fields.Datetime(string='Site Visit Date')
    briefing_date = fields.Datetime(string='Briefing Session Date')

    province = fields.Char(string='Province')
    ocds_category = fields.Char(string='OCDS Category', help='Category from the eTenders OCDS API')
    tender_value = fields.Monetary(string='Estimated Value', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    status = fields.Selection([
        ('new', 'New'),
        ('matched', 'Matched'),
        ('imported', 'Imported'),
        ('archived', 'Archived'),
    ], string='Status', default='new', tracking=True)

    raw_data = fields.Text(string='Raw API Data')
    url = fields.Char(string='Source URL')
    embedding = fields.Text(string='Embedding', readonly=True,
                            help='Pre-computed NLP embedding vector')
    embedding_date = fields.Datetime(string='Embedding Date', readonly=True)

    match_ids = fields.One2many('tender.feed.match', 'feed_id', string='Matches')
    match_count = fields.Integer(compute='_compute_match_count', string='Match Count')
    best_score = fields.Float(compute='_compute_best_score', string='Best Match Score', aggregator='max')
    imported_tender_id = fields.Many2one('tender.tender', string='Imported Tender', readonly=True, copy=False)
    keyword_config_ids = fields.Many2many('tender.feed.keyword.config',
                                          'tender_feed_keyword_config_rel',
                                          'feed_id', 'config_id',
                                          string='Matched Keyword Configs')

    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('external_source_unique', 'UNIQUE(external_id, source)',
         'A tender with this external ID from the same source already exists!'),
    ]

    @api.depends('match_ids')
    def _compute_match_count(self):
        for f in self:
            f.match_count = len(f.match_ids)

    @api.depends('match_ids', 'match_ids.similarity_score')
    def _compute_best_score(self):
        for f in self:
            scores = f.match_ids.mapped('similarity_score')
            f.best_score = max(scores) if scores else 0.0

    def _get_embedding_text(self):
        parts = []
        if self.description_text:
            parts.append(self.description_text)
        elif self.description:
            import re
            plain = re.sub(r'<[^>]+>', '', self.description)
            parts.append(plain)
        if self.name:
            parts.insert(0, self.name)
        if self.issuer_name:
            parts.append(f"Issuer: {self.issuer_name}")
        return '\n'.join(parts)

    def _compute_embedding(self):
        self.ensure_one()
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            return False
        text = self._get_embedding_text()
        if not text.strip():
            return False
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            vector = model.encode(text)
            self.embedding = ','.join(str(x) for x in vector)
            self.embedding_date = fields.Datetime.now()
            return True
        except Exception as e:
            _logger.error("Feed embedding failed for %s: %s", self.name, e)
            return False

    def action_compute_embedding(self):
        for feed in self:
            feed._compute_embedding()
        return True

    def action_import_to_tender(self):
        self.ensure_one()
        tender = self.env['tender.tender'].create({
            'name': self.name,
            'tender_number': self.tender_number,
            'description': self.description,
            'deadline_submission': self.deadline_submission,
            'date_published': self.date_published,
            'date_site_visit': self.site_visit_date,
            'date_briefing': self.briefing_date,
            'category_id': self.category_id.id,
            'issuer_id': self.issuer_id.id if self.issuer_id else None,
        })
        if self.issuer_name and not self.issuer_id:
            partner = self.env['res.partner'].search([('name', 'ilike', self.issuer_name)], limit=1)
            if not partner:
                partner = self.env['res.partner'].create({
                    'name': self.issuer_name,
                    'is_company': True,
                })
            tender.issuer_id = partner
        self.imported_tender_id = tender
        self.status = 'imported'
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tender'),
            'res_model': 'tender.tender',
            'res_id': tender.id,
            'view_mode': 'form',
        }

    def action_run_matching(self):
        profiles = self.env['tender.company.profile'].search([('active', '=', True)])
        for feed in self:
            feed._match_against_profiles(profiles)
        return True

    def _match_against_profiles(self, profiles):
        self.ensure_one()
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            _logger.warning("sentence-transformers not installed, skipping matching")
            return
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
            feed_text = self._get_embedding_text()
            if not feed_text.strip():
                return
            feed_vec = model.encode(feed_text)
            for profile in profiles:
                profile_text = profile._get_embedding_text()
                if not profile_text.strip():
                    continue
                profile_vec = model.encode(profile_text)
                score = self._cosine_similarity(feed_vec, profile_vec)
                if score >= 0.3:
                    existing = self.env['tender.feed.match'].search([
                        ('feed_id', '=', self.id),
                        ('company_profile_id', '=', profile.id),
                    ], limit=1)
                    if existing:
                        existing.similarity_score = score
                    else:
                        self.env['tender.feed.match'].create({
                            'feed_id': self.id,
                            'company_profile_id': profile.id,
                            'similarity_score': score,
                        })
            if self.match_ids:
                self.status = 'matched'
        except Exception as e:
            _logger.error("Matching failed for feed %s: %s", self.name, e)

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        import numpy as np
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot = np.dot(v1, v2)
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        return float(dot / norm) if norm else 0.0

    @api.model
    def cron_fetch_etenders(self, days_back=7):
        """Fetch open tenders from the official eTenders OCDS API (free, no auth)."""
        try:
            import requests
            from datetime import datetime, timedelta

            now = datetime.utcnow()
            date_from = (now - timedelta(days=days_back)).strftime('%Y-%m-%d')
            date_to = now.strftime('%Y-%m-%d')

            page = 1
            page_size = 500
            imported = 0
            seen = set()

            while True:
                resp = requests.get(
                    'https://ocds-api.etenders.gov.za/api/OCDSReleases',
                    params={
                        'PageNumber': page,
                        'PageSize': page_size,
                        'dateFrom': date_from,
                        'dateTo': date_to,
                    },
                    timeout=60,
                )
                if resp.status_code == 400:
                    _logger.warning("eTenders API 400: %s", resp.text)
                    break
                resp.raise_for_status()
                data = resp.json()
                releases = data.get('releases', [])
                if not releases:
                    break

                for release in releases:
                    tender = release.get('tender') or {}
                    if tender.get('status') != 'active':
                        continue
                    ocid = release.get('ocid', '')
                    if ocid in seen:
                        continue
                    seen.add(ocid)
                    try:
                        self._import_ocds_release(release)
                        imported += 1
                    except Exception as e:
                        _logger.error("Failed to import OCDS release %s: %s", ocid, e)

                links = data.get('links', {})
                next_url = links.get('next') if isinstance(links, dict) else None
                if not next_url:
                    break
                page += 1

            _logger.info("eTenders OCDS import complete: %d tenders processed", imported)
            return True
        except ImportError:
            _logger.error("requests library required for API fetch")
            return False
        except Exception as e:
            _logger.error("eTenders OCDS fetch failed: %s", e)
            return False

    @api.model
    def cron_fetch_keyword_tenders(self, config_ids=None):
        """Fetch fresh tenders, then filter by company profile service category
        keywords and any preconfigured keyword configs (linked or standalone).

        If config_ids is given, only those specific configs are processed.
        Otherwise, all active company profiles are auto-searched.
        """
        kw_config_model = self.env['tender.feed.keyword.config']

        if config_ids is not None:
            configs = kw_config_model.browse(config_ids)
        else:
            configs = kw_config_model.search([('active', '=', True)])

        # Refresh feed data
        self.cron_fetch_etenders(days_back=7)
        now = fields.Datetime.now()

        if config_ids is not None:
            # Legacy mode: process specific configs only
            self._apply_keyword_configs(configs, now)
        else:
            # Auto mode: search using company profile keywords + linked configs
            configs_already_processed = set()
            profiles = self.env['tender.company.profile'].search([('active', '=', True)])
            for profile in profiles:
                all_keywords = profile._get_all_keywords()
                if not all_keywords:
                    continue
                matching = self._search_feeds_by_keywords(
                    all_keywords, min_days=profile.min_days_to_deadline or None
                )
                if matching:
                    # Link feeds to the profile's keyword configs
                    for config in profile.keyword_config_ids:
                        configs_already_processed.add(config.id)
                        linked = matching.filtered(lambda f: config.id not in f.keyword_config_ids.ids)
                        for feed in linked:
                            feed.write({'keyword_config_ids': [(4, config.id)]})
                    # Run NLP matching
                    for feed in matching:
                        feed._match_against_profiles(profile)
                    _logger.info(
                        "Profile '%s': %d matching feeds from %d keywords",
                        profile.partner_id.display_name, len(matching), len(all_keywords)
                    )

            # Also process any standalone configs not linked to a profile
            standalone = configs - kw_config_model.browse(list(configs_already_processed))
            if standalone:
                self._apply_keyword_configs(standalone, now)

        return True

    @api.model
    def _apply_keyword_configs(self, configs, now=None):
        """Apply keyword matching for specific config records."""
        if now is None:
            now = fields.Datetime.now()
        for config in configs:
            keywords = [k.strip().lower() for k in config.keywords.split(',') if k.strip()]
            if not keywords:
                continue
            matching = self._search_feeds_by_keywords(
                keywords, min_days=config.min_days_to_deadline or None
            )
            for feed in matching:
                if config.id not in feed.keyword_config_ids.ids:
                    feed.write({'keyword_config_ids': [(4, config.id)]})
            config.write({'last_fetch_date': now})
            _logger.info("Keyword config '%s': %d matching feeds", config.name, len(matching))

    @api.model
    def _search_feeds_by_keywords(self, keywords, min_days=None):
        """Search all etender feeds matching any of the given keywords.

        :param keywords: list of lowercase keyword strings to match
        :param min_days: optional int — only return feeds whose deadline
                         is at least this many days from now (allows time
                         to evaluate and prepare submissions)
        """
        def kw_matches(feed):
            cat = (feed.ocds_category or '').lower()
            name = (feed.name or '').lower()
            desc = (feed.description_text or '')[:1000].lower()
            return any(kw in cat or kw in name or kw in desc for kw in keywords)

        feeds = self.search([('source', '=', 'etender')]).filtered(kw_matches)

        if min_days:
            cutoff = datetime.utcnow() + timedelta(days=min_days)
            feeds = feeds.filtered(
                lambda f: f.deadline_submission and f.deadline_submission >= cutoff
            )

        return feeds

    @api.model
    def _import_ocds_release(self, release):
        """Import a single OCDS release from the eTenders API."""
        ocid = release.get('ocid', '')
        existing = self.search([('external_id', '=', ocid), ('source', '=', 'etender')], limit=1)
        if existing:
            return existing

        tender = release.get('tender') or {}
        buyer = release.get('buyer') or {}

        # Title
        title = tender.get('title', '') or ''
        if not title.strip():
            title = f"Tender {ocid}"

        # Description
        description = tender.get('description', '') or ''
        description_text = description

        # Tender period
        tender_period = tender.get('tenderPeriod') or {}
        deadline = None
        date_published = None
        if tender_period.get('endDate'):
            try:
                deadline = tender_period['endDate'].replace('Z', '+00:00')
                deadline = datetime.fromisoformat(deadline)
            except Exception:
                pass
        if tender_period.get('startDate'):
            try:
                date_published = tender_period['startDate'].replace('Z', '+00:00')
                date_published = datetime.fromisoformat(date_published).date()
            except Exception:
                pass

        # Value
        value_obj = tender.get('value') or {}
        tender_value = value_obj.get('amount', 0) or 0

        # Issuer
        issuer_name = buyer.get('name', '') or ''
        procuring_entity = tender.get('procuringEntity') or {}
        if not issuer_name and procuring_entity:
            issuer_name = procuring_entity.get('name', '') or ''

        # Province & Category
        province = tender.get('province', '') or ''
        ocds_category = tender.get('category', '') or ''
        if province:
            description_text = f"[{province}] {description_text}" if description_text else province

        # Tender number — use OCID suffix or tender.id
        tender_number = tender.get('id', '') or ocid.split('-')[-1] if '-' in ocid else ocid

        # URL on eTenders
        tender_url = ''
        docs = tender.get('documents') or []
        if isinstance(docs, list) and docs:
            for doc in docs:
                if isinstance(doc, dict) and doc.get('url'):
                    tender_url = doc['url']
                    break

        vals = {
            'name': title,
            'external_id': ocid,
            'source': 'etender',
            'tender_number': tender_number,
            'issuer_name': issuer_name,
            'description': description,
            'description_text': description_text,
            'deadline_submission': deadline,
            'date_published': date_published,
            'tender_value': tender_value if tender_value else False,
            'province': province,
            'ocds_category': ocds_category,
            'url': tender_url,
            'raw_data': json.dumps(release),
        }

        feed = self.create(vals)
        try:
            feed._compute_embedding()
        except Exception:
            pass
        return feed
