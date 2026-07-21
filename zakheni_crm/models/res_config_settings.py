from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    crm_auto_assign_territory = fields.Boolean(
        "Auto-Assign Territory",
        default=False,
        config_parameter="zakheni_crm.auto_assign_territory",
    )
    crm_auto_score_leads = fields.Boolean(
        "Auto-Score Leads",
        default=True,
        config_parameter="zakheni_crm.auto_score_leads",
    )
    crm_enable_sla_tracking = fields.Boolean(
        "Enable SLA Tracking",
        default=False,
        config_parameter="zakheni_crm.enable_sla_tracking",
    )
    crm_default_forecast_model = fields.Selection([
        ("optimistic", "Optimistic"),
        ("pessimistic", "Pessimistic"),
        ("most_likely", "Most Likely"),
    ], string="Default Forecast Model",
        default="most_likely",
        config_parameter="zakheni_crm.default_forecast_model",
    )
