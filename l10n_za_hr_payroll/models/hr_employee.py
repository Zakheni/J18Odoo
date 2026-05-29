from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    l10n_za_id_number = fields.Char(
        string="SA ID Number",
        size=13,
        help="South African 13-digit identity number.",
    )
    l10n_za_tax_number = fields.Char(
        string="Tax Reference Number",
        help="SARS Income Tax reference number.",
    )
    l10n_za_passport_number = fields.Char(
        string="Passport Number",
        help="Passport number for foreign nationals.",
    )
    l10n_za_medical_aid_dependents = fields.Integer(
        string="Medical Aid Dependents",
        default=0,
        help="Number of dependents on medical aid (excluding main member).",
    )
