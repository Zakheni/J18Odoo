import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    _logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")


class TenderCompanyProfile(models.Model):
    _name = 'tender.company.profile'
    _description = 'Company Profile'
    _inherit = ['mail.thread']
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner', string='Company', required=True, ondelete='cascade',
                                 default=lambda self: self.env.company.partner_id)
    active = fields.Boolean(default=True)

    sector = fields.Selection([
        ('construction', 'Construction'),
        ('engineering', 'Engineering'),
        ('information_technology', 'Information Technology'),
        ('consulting', 'Consulting'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('transport', 'Transport & Logistics'),
        ('manufacturing', 'Manufacturing'),
        ('energy', 'Energy'),
        ('agriculture', 'Agriculture'),
        ('financial_services', 'Financial Services'),
        ('telecommunications', 'Telecommunications'),
        ('security', 'Security'),
        ('environmental', 'Environmental'),
        ('other', 'Other'),
    ], string='Primary Sector', tracking=True)

    bee_level = fields.Selection([
        ('1', 'Level 1 (135% B-BBEE)'),
        ('2', 'Level 2 (125% B-BBEE)'),
        ('3', 'Level 3 (110% B-BBEE)'),
        ('4', 'Level 4 (100% B-BBEE)'),
        ('5', 'Level 5 (80% B-BBEE)'),
        ('6', 'Level 6 (60% B-BBEE)'),
        ('7', 'Level 7 (50% B-BBEE)'),
        ('8', 'Level 8 (10% B-BBEE)'),
        ('non_compliant', 'Non-Compliant'),
        ('exempted', 'Exempted Micro Enterprise (EME)'),
        ('qualifying_small', 'Qualifying Small Enterprise (QSE)'),
    ], string='B-BBEE Level', tracking=True)

    procurement_recognised_level = fields.Char(
        string='Procurement Recognition Level',
        help='Automatically computed based on B-BBEE level and recognition of gender/black ownership level')

    service_category_ids = fields.Many2many(
        'tender.service.category',
        'company_profile_service_category_rel',
        'profile_id', 'category_id',
        string='Service Categories')

    region_ids = fields.Many2many(
        'res.country.state',
        'company_profile_region_rel',
        'profile_id', 'state_id',
        string='Service Regions',
        domain=[('country_id.code', '=', 'ZA')])

    min_project_value = fields.Monetary(string='Min Project Value', currency_field='currency_id')
    max_project_value = fields.Monetary(string='Max Project Value', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    employee_count = fields.Integer(string='Number of Employees')
    years_in_business = fields.Integer(string='Years in Business')
    annual_turnover = fields.Monetary(string='Annual Turnover', currency_field='currency_id')

    description = fields.Text(string='Company Capabilities',
                              help='Describe your company capabilities, expertise, and key differentiators. Used for AI matching.')

    embedding = fields.Text(string='Profile Embedding', readonly=True,
                            help='Pre-computed NLP embedding vector for similarity matching')
    embedding_date = fields.Datetime(string='Embedding Last Computed', readonly=True)

    match_ids = fields.One2many('tender.feed.match', 'company_profile_id', string='Tender Matches')
    match_count = fields.Integer(compute='_compute_match_count', string='Matched Tenders')

    keyword_config_ids = fields.One2many('tender.feed.keyword.config', 'profile_id',
                                         string='Preconfigured Keywords')

    min_days_to_deadline = fields.Integer(
        string='Min Days to Deadline',
        default=14,
        help='Only match tenders with at least this many days until the submission deadline. '
             'This ensures you have enough time to evaluate and prepare a bid.')

    @api.depends('match_ids')
    def _compute_match_count(self):
        for p in self:
            p.match_count = len(p.match_ids)

    def _get_embedding_text(self):
        parts = []
        if self.description:
            parts.append(self.description)
        if self.sector:
            parts.append(f"Sector: {dict(self._fields['sector'].selection).get(self.sector, '')}")
        if self.service_category_ids:
            parts.append(f"Services: {', '.join(self.service_category_ids.mapped('name'))}")
        if self.region_ids:
            parts.append(f"Regions: {', '.join(self.region_ids.mapped('name'))}")
        return '\n'.join(parts)

    def _compute_embedding(self):
        self.ensure_one()
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            _logger.warning("Cannot compute embedding: sentence-transformers not installed")
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
            _logger.error("Embedding computation failed: %s", e)
            return False

    def action_compute_embedding(self):
        for profile in self:
            profile._compute_embedding()
        return True

    def _get_all_keywords(self):
        """Collect all search keywords from service categories and keyword configs."""
        keywords = set()
        for cat in self.service_category_ids:
            if cat.ocds_keywords:
                for kw in cat.ocds_keywords.split(','):
                    kw = kw.strip().lower()
                    if kw:
                        keywords.add(kw)
        for config in self.keyword_config_ids:
            if config.active and config.keywords:
                for kw in config.keywords.split(','):
                    kw = kw.strip().lower()
                    if kw:
                        keywords.add(kw)
        return sorted(keywords)

    def action_find_matching_tenders(self):
        """Refresh tender feeds from eTenders, filter by this profile's
        service category keywords and preconfigured keyword configs,
        then run NLP similarity matching."""
        self.ensure_one()

        all_keywords = self._get_all_keywords()
        if not all_keywords:
            raise UserError(_(
                "No keywords found. Add OCDS Search Keywords to Service Categories "
                "or create Preconfigured Keywords under this profile."
            ))

        # Import latest tenders from OCDS API
        self.env['tender.feed'].cron_fetch_etenders(days_back=7)

        # Use the shared search method with deadline filter
        matching = self.env['tender.feed']._search_feeds_by_keywords(
            all_keywords, min_days=self.min_days_to_deadline or None
        )

        if not matching:
            raise UserError(_("No tenders found matching your profile keywords."))

        # Run matching against this profile
        for feed in matching:
            feed._match_against_profiles(self)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Matching Tenders'),
            'res_model': 'tender.feed',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', matching.ids)],
            'context': {'create': False},
        }

    @api.model
    def get_or_create_profile(self, partner_id=None):
        if not partner_id:
            partner_id = self.env.company.partner_id.id
        profile = self.search([('partner_id', '=', partner_id)], limit=1)
        if not profile:
            profile = self.create({'partner_id': partner_id})
        return profile
