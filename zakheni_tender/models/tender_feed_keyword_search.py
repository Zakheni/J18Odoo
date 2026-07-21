import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TenderFeedKeywordSearch(models.TransientModel):
    _name = 'tender.feed.keyword.search'
    _description = 'Keyword Search on eTenders'

    keywords = fields.Char(string='Keywords', required=True,
                           help='Comma-separated keywords to search tender titles and categories on eTenders.gov.za')
    days_back = fields.Integer(string='Look Back (days)', default=7,
                               help='Number of days to look back for tenders')

    def action_fetch(self):
        self.ensure_one()
        if not self.keywords.strip():
            raise UserError(_("Please enter at least one keyword."))

        keywords = [k.strip().lower() for k in self.keywords.split(',') if k.strip()]
        feed_model = self.env['tender.feed']

        # Refresh from OCDS API
        try:
            feed_model.cron_fetch_etenders(days_back=self.days_back)
        except Exception as e:
            _logger.error("eTenders fetch failed: %s", e)

        def kw_matches(feed):
            cat = (feed.ocds_category or '').lower()
            name = (feed.name or '').lower()
            desc = (feed.description_text or feed.description or '').lower()
            return any(kw in cat or kw in name or kw in desc for kw in keywords)

        all_feeds = feed_model.search([('source', '=', 'etender')])
        matching = all_feeds.filtered(kw_matches)

        if not matching:
            raise UserError(_("No tenders found matching '%s'.") % self.keywords)

        return {
            'type': 'ir.actions.act_window',
            'name': _('Keyword Search Results'),
            'res_model': 'tender.feed',
            'view_mode': 'kanban,list,form',
            'domain': [('id', 'in', matching.ids)],
            'context': {'create': False},
        }
