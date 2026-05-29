from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_za_paye_number = fields.Char(
        string="PAYE Reference Number",
        help="SARS PAYE (employees tax) reference number.",
    )
    l10n_za_uif_number = fields.Char(
        string="UIF Reference Number",
        help="SARS UIF reference number.",
    )
    l10n_za_sdl_number = fields.Char(
        string="SDL Reference Number",
        help="SARS SDL reference number.",
    )
    l10n_za_sars_registration_number = fields.Char(
        string="SARS Registration Number",
        help="SARS registered tax payer number.",
    )
    l10n_za_site_number = fields.Char(
        string="SITE Number",
        help="Standard Income Tax on Employees number (if applicable).",
    )
