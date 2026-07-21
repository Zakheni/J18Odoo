from odoo import api, fields, models


class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    lead_score = fields.Integer('Lead Score', default=0)
    last_open_date = fields.Datetime('Last Email Open')
    last_click_date = fields.Datetime('Last Link Click')
    last_conversion_date = fields.Datetime('Last Conversion')
    total_opens = fields.Integer('Total Opens', default=0)
    total_clicks = fields.Integer('Total Clicks', default=0)
    total_conversions = fields.Integer('Total Conversions', default=0)
    is_engaged = fields.Boolean('Engaged', compute='_compute_engagement')
    engagement_score = fields.Float('Engagement Score', compute='_compute_engagement')
    subscription_preference_ids = fields.One2many(
        'marketing.subscription.preference', 'contact_id',
        string='Subscription Preferences')
    reengagement_campaign_ids = fields.Many2many(
        'marketing.reengagement', string='Re-engagement Campaigns')

    @api.depends('total_opens', 'total_clicks', 'total_conversions', 'lead_score')
    def _compute_engagement(self):
        for contact in self:
            score = 0.0
            score += min(contact.total_opens * 2.0, 20.0)
            score += min(contact.total_clicks * 3.0, 30.0)
            score += min(contact.total_conversions * 10.0, 50.0)
            score += min(contact.lead_score * 0.5, 20.0)
            contact.engagement_score = score
            contact.is_engaged = score >= 25.0

    def action_view_subscription_preferences(self):
        self.ensure_one()
        return {
            'name': 'Subscription Preferences',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'marketing.subscription.preference',
            'domain': [('contact_id', '=', self.id)],
            'context': {'default_contact_id': self.id},
        }
