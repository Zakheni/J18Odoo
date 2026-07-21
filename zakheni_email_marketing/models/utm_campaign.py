from odoo import api, fields, models


class UtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    marketing_campaign_id = fields.Many2one(
        'marketing.campaign', string='Marketing Campaign',
        ondelete='set null')
    is_ab_test = fields.Boolean('A/B Test Campaign', default=False)
    ab_test_winner_selection = fields.Selection([
        ('opened_ratio', 'Open Rate'),
        ('clicked_ratio', 'Click Rate'),
        ('replied_ratio', 'Reply Rate'),
        ('conversion_ratio', 'Conversion Rate'),
        ('manual', 'Manual Selection'),
    ], string='A/B Test Winner Selection', default='opened_ratio')
    ab_test_schedule_datetime = fields.Datetime('A/B Test Schedule')
    ab_test_winner_mailing_id = fields.Many2one(
        'mailing.mailing', string='Winner Mailing')
    ab_testing_completed = fields.Boolean('A/B Testing Completed', default=False)
    ab_testing_mailings_count = fields.Integer(
        'A/B Test Mailings', compute='_compute_ab_testing_mailings_count')

    def _compute_ab_testing_mailings_count(self):
        for campaign in self:
            campaign.ab_testing_mailings_count = len(campaign.mailing_mail_ids.filtered('ab_testing_enabled'))
