from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cash_forecast_days = fields.Integer(
        string='Cash Forecast Horizon (days)',
        default=90,
        config_parameter='zakheni_accounting.cash_forecast_days',
    )
    enable_auto_followup = fields.Boolean(
        string='Enable Automatic Follow-up',
        default=True,
        config_parameter='zakheni_accounting.enable_auto_followup',
    )
    followup_cron_interval = fields.Integer(
        string='Follow-up Cron Interval (days)',
        default=1,
        config_parameter='zakheni_accounting.followup_cron_interval',
    )
