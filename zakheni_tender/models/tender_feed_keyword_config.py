import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class TenderFeedKeywordConfig(models.Model):
    _name = 'tender.feed.keyword.config'
    _description = 'Persistent Keyword Search Config'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    keywords = fields.Char(string='Keywords', required=True,
                           help='Comma-separated keywords to search tender titles, descriptions, and categories')
    profile_id = fields.Many2one('tender.company.profile', string='Company Profile',
                                 ondelete='cascade',
                                 help='Link to a company profile. If set, this config is used when auto-searching for that profile.')
    active = fields.Boolean(default=True)
    last_fetch_date = fields.Datetime(string='Last Fetched', readonly=True)
    feed_count = fields.Integer(compute='_compute_feed_count', string='Matched Feeds')

    min_days_to_deadline = fields.Integer(
        string='Min Days to Deadline',
        default=14,
        help='Only match tenders with at least this many days until the submission deadline. '
             'Leave at 0 or 14+ to ensure enough time to evaluate and prepare a bid.')

    def _compute_feed_count(self):
        for rec in self:
            rec.feed_count = len(rec.feed_ids)

    feed_ids = fields.Many2many('tender.feed', 'tender_feed_keyword_config_rel',
                                'config_id', 'feed_id', string='Matched Feeds')

    def action_run_now(self):
        """Run keyword search immediately for selected configs."""
        return self.env['tender.feed'].cron_fetch_keyword_tenders(config_ids=self.ids)

    def action_view_feeds(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Matched Feeds: %s') % self.name,
            'res_model': 'tender.feed',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', self.feed_ids.ids)],
        }
