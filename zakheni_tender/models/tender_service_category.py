import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class TenderServiceCategory(models.Model):
    _name = 'tender.service.category'
    _description = 'Service Category'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
    parent_id = fields.Many2one('tender.service.category', string='Parent Category', ondelete='restrict')
    child_ids = fields.One2many('tender.service.category', 'parent_id', string='Subcategories')

    ocds_keywords = fields.Char(
        string='OCDS Search Keywords',
        help='Comma-separated keywords to match against OCDS API tender categories. '
             'E.g. "Construction, Infrastructure" for a Construction category.')

    def action_search_etenders(self):
        """Search existing tender feeds matching this category's OCDS keywords.
        First fetches fresh data via the cron, then filters by category keywords.
        """
        self.ensure_one()
        if not self.ocds_keywords and not self.name:
            raise UserError(_("Please set OCDS Search Keywords on this category first."))

        keywords = [k.strip().lower() for k in (self.ocds_keywords or self.name).split(',')]
        feed_model = self.env['tender.feed']

        import requests
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        date_from = (now - timedelta(days=7)).strftime('%Y-%m-%d')
        date_to = now.strftime('%Y-%m-%d')

        def keyword_matches(category):
            return any(kw in (category or '').lower() for kw in keywords)

        # Refresh feeds from OCDS API (the cron method handles pagination)
        try:
            feed_model.cron_fetch_etenders(days_back=7)
        except Exception as e:
            _logger.error("eTenders fetch failed: %s", e)

        # Find matching feeds by ocds_category
        all_feeds = feed_model.search([('source', '=', 'etender')])
        matching = all_feeds.filtered(lambda f: keyword_matches(f.ocds_category))
        # Also match newly created feeds that haven't been returned yet — check description_text too
        if not matching:
            matching = all_feeds.filtered(
                lambda f: keyword_matches(f.ocds_category) or keyword_matches(f.name)
            )

        if matching:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Matching Tenders'),
                'res_model': 'tender.feed',
                'view_mode': 'kanban,list,form',
                'domain': [('id', 'in', matching.ids)],
                'context': {'create': False},
            }

        raise UserError(_("No tenders found matching '%s'. Try refreshing the feed first.") % self.name)
