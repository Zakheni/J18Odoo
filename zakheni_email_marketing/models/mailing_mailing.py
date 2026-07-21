from odoo import api, fields, models


class MassMailing(models.Model):
    _inherit = 'mailing.mailing'

    zakheni_campaign_id = fields.Many2one(
        'marketing.campaign', string='Marketing Campaign',
        ondelete='set null', index=True)
    zakheni_campaign_step_id = fields.Many2one(
        'marketing.campaign.step', string='Campaign Step',
        ondelete='set null')

    reengagement_id = fields.Many2one(
        'marketing.reengagement', string='Re-engagement Campaign',
        ondelete='set null')

    is_automated = fields.Boolean('Automated Email', default=False)
    automation_rule_id = fields.Many2one(
        'marketing.automation', string='Automation Rule',
        ondelete='set null')

    landing_page_id = fields.Many2one(
        'marketing.landing.page', string='Landing Page',
        ondelete='set null')

    is_ab_test_mailing = fields.Boolean('A/B Test Variant', default=False)
    ab_test_group = fields.Char('A/B Test Group')
    ab_test_metric = fields.Selection([
        ('opened_ratio', 'Open Rate'),
        ('clicked_ratio', 'Click Rate'),
        ('replied_ratio', 'Reply Rate'),
        ('conversion_ratio', 'Conversion Rate'),
    ], string='A/B Test Metric', default='opened_ratio')

    conversion_count = fields.Integer(
        'Conversions', compute='_compute_ab_test_extended')
    conversion_ratio = fields.Float(
        'Conversion Rate', compute='_compute_ab_test_extended')

    roi_value = fields.Float(
        'ROI Value', compute='_compute_roi')
    roi_cost = fields.Float(
        'ROI Cost', compute='_compute_roi')
    roi_percentage = fields.Float(
        'ROI %', compute='_compute_roi')

    def _compute_ab_test_extended(self):
        for mailing in self:
            conversions = len(mailing.mailing_trace_ids.filtered(
                lambda t: t.zakheni_conversion_date))
            total = mailing.sent or 1
            mailing.conversion_count = conversions
            mailing.conversion_ratio = round(100.0 * conversions / total, 2)

    def _compute_roi(self):
        for mailing in self:
            mailing.roi_value = 0.0
            mailing.roi_cost = 0.0
            mailing.roi_percentage = 0.0
            traces = mailing.mailing_trace_ids
            conversions = traces.filtered(lambda t: t.zakheni_conversion_date)
            if conversions and hasattr(conversions, 'zakheni_conversion_amount'):
                total_value = sum(conversions.mapped('zakheni_conversion_amount') or [0])
                mailing.roi_value = total_value
            cost = 0.0
            if mailing.mail_server_id:
                cost = 0.01 * mailing.sent
            mailing.roi_cost = cost
            if cost and mailing.roi_value:
                mailing.roi_percentage = round(
                    (mailing.roi_value - cost) / cost * 100, 2)

    def action_view_roi_analysis(self):
        self.ensure_one()
        return {
            'name': 'ROI Analysis',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'marketing.roi',
            'context': {
                'default_mailing_id': self.id,
                'default_name': self.subject,
            },
        }
