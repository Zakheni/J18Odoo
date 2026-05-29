from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    l10n_za_tax_rebate = fields.Selection(
        [("primary", "Primary"), ("secondary", "Secondary (65+)"), ("tertiary", "Tertiary (75+)")],
        string="Tax Rebate",
        default="primary",
        help="South African tax rebate category based on age.",
    )
    l10n_za_medical_aid_employee_contrib = fields.Float(
        string="Medical Aid Employee Contribution",
        digits="Payroll",
        help="Monthly employee contribution to medical aid.",
    )
    l10n_za_medical_aid_dependents = fields.Integer(
        string="Medical Aid Dependents",
        default=0,
        help="Number of dependents on medical aid (excluding main member).",
    )
    l10n_za_pension_fund_id = fields.Many2one(
        "hr.contribution.register",
        string="Pension Fund",
        domain="[('partner_id', '!=', False)]",
        help="Employee's pension fund.",
    )
    l10n_za_pension_employee_rate = fields.Float(
        string="Pension Employee Rate (%)",
        digits="Payroll Rate",
        default=7.5,
        help="Employee pension contribution as percentage of basic.",
    )
    l10n_za_pension_employer_rate = fields.Float(
        string="Pension Employer Rate (%)",
        digits="Payroll Rate",
        default=7.5,
        help="Employer pension contribution as percentage of basic.",
    )
    l10n_za_provident_fund_id = fields.Many2one(
        "hr.contribution.register",
        string="Provident Fund",
        domain="[('partner_id', '!=', False)]",
    )
    l10n_za_provident_employee_rate = fields.Float(
        string="Provident Employee Rate (%)",
        digits="Payroll Rate",
        default=0.0,
    )
    l10n_za_provident_employer_rate = fields.Float(
        string="Provident Employer Rate (%)",
        digits="Payroll Rate",
        default=0.0,
    )
    l10n_za_travel_allowance = fields.Float(
        string="Travel Allowance",
        digits="Payroll",
        help="Monthly travel allowance.",
    )
    l10n_za_housing_allowance = fields.Float(
        string="Housing Allowance",
        digits="Payroll",
        help="Monthly housing or subsistence allowance.",
    )
    l10n_za_car_allowance = fields.Float(
        string="Car Allowance",
        digits="Payroll",
        help="Monthly car allowance.",
    )
    l10n_za_other_allowance = fields.Float(
        string="Other Allowance",
        digits="Payroll",
        help="Monthly other taxable allowance.",
    )
    l10n_za_uif_applies = fields.Boolean(
        string="UIF Applicable",
        default=True,
        help="Whether UIF deductions apply to this employee.",
    )
    l10n_za_sdl_applies = fields.Boolean(
        string="SDL Applicable",
        default=True,
        help="Whether SDL deductions apply to this employee.",
    )
