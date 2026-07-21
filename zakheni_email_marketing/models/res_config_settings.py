from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zakheni_marketing_default_cost_per_email = fields.Float(
        'Default Cost per Email',
        default=0.01,
        config_parameter='zakheni_email_marketing.default_cost_per_email')
    zakheni_marketing_enable_lead_scoring = fields.Boolean(
        'Enable Lead Scoring',
        default=True,
        config_parameter='zakheni_email_marketing.enable_lead_scoring')
    zakheni_marketing_enable_automation = fields.Boolean(
        'Enable Marketing Automation',
        default=True,
        config_parameter='zakheni_email_marketing.enable_automation')
    zakheni_marketing_enable_reengagement = fields.Boolean(
        'Enable Re-engagement Campaigns',
        default=True,
        config_parameter='zakheni_email_marketing.enable_reengagement')
    zakheni_marketing_auto_sync_segments = fields.Boolean(
        'Auto-Sync Segments',
        default=True,
        config_parameter='zakheni_email_marketing.auto_sync_segments')
