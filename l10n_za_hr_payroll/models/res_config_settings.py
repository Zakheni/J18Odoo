from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    l10n_za_paye_number = fields.Char(
        related="company_id.l10n_za_paye_number", readonly=False
    )
    l10n_za_uif_number = fields.Char(
        related="company_id.l10n_za_uif_number", readonly=False
    )
    l10n_za_sdl_number = fields.Char(
        related="company_id.l10n_za_sdl_number", readonly=False
    )
    l10n_za_sars_registration_number = fields.Char(
        related="company_id.l10n_za_sars_registration_number", readonly=False
    )
