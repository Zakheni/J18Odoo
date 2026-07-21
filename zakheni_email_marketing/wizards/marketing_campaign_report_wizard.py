from odoo import api, fields, models


class MarketingCampaignReportWizard(models.TransientModel):
    _name = 'marketing.campaign.report.wizard'
    _description = 'Marketing Campaign Report Wizard'

    date_from = fields.Date('From Date', required=True)
    date_to = fields.Date('To Date', required=True)
    campaign_ids = fields.Many2many('marketing.campaign', string='Campaigns')
    report_type = fields.Selection([
        ('summary', 'Summary Report'),
        ('detailed', 'Detailed Report'),
        ('roi', 'ROI Analysis'),
    ], string='Report Type', default='summary', required=True)

    def action_generate_report(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Campaign Report',
            'view_mode': 'tree,form',
            'res_model': 'marketing.roi',
            'domain': [('campaign_id', 'in', self.campaign_ids.ids)] if self.campaign_ids else [],
            'context': {
                'search_default_group_campaign': True,
            },
        }
