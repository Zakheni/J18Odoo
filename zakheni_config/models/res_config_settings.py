from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tax_table_autofetch_url = fields.Char(
        related="company_id.tax_table_autofetch_url",
        readonly=False,
    )
    tax_table_autofetch_enabled = fields.Boolean(
        related="company_id.tax_table_autofetch_enabled",
        readonly=False,
    )
