import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class TenderFeedMatch(models.Model):
    _name = 'tender.feed.match'
    _description = 'Tender Feed Match'
    _order = 'similarity_score desc, create_date desc'

    feed_id = fields.Many2one('tender.feed', string='Tender Feed', required=True, ondelete='cascade')
    company_profile_id = fields.Many2one('tender.company.profile', string='Company Profile',
                                         required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='company_profile_id.partner_id', string='Company', store=True)
    similarity_score = fields.Float(string='Similarity Score', aggregator='max')
    score_display = fields.Char(compute='_compute_score_display', string='Score')

    match_date = fields.Datetime(string='Match Date', default=fields.Datetime.now, readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
    ], string='Status', default='pending', tracking=True)

    notes = fields.Text(string='Notes')

    @api.depends('similarity_score')
    def _compute_score_display(self):
        for m in self:
            m.score_display = f'{m.similarity_score:.1%}' if m.similarity_score else '0%'

    def action_reviewed(self):
        self.state = 'reviewed'

    def action_interested(self):
        self.state = 'interested'
        self.feed_id.status = 'matched'
        if not self.feed_id.imported_tender_id:
            self.feed_id.action_import_to_tender()

    def action_not_interested(self):
        self.state = 'not_interested'

    @api.model
    def cron_compute_matches(self):
        profiles = self.env['tender.company.profile'].search([('active', '=', True)])
        if not profiles:
            _logger.warning("No active company profiles found for matching")
            return False
        feeds = self.env['tender.feed'].search([
            ('active', '=', True),
            ('status', 'in', ('new', 'matched')),
            '|', ('deadline_submission', '>=', fields.Datetime.now()), ('deadline_submission', '=', False),
        ])
        for feed in feeds:
            feed._match_against_profiles(profiles)
        return True
