import math
from datetime import date

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    l10n_za_paye_amount = fields.Float(
        string="PAYE", compute="_compute_l10n_za_totals", store=False
    )
    l10n_za_uif_amount = fields.Float(
        string="UIF", compute="_compute_l10n_za_totals", store=False
    )
    l10n_za_sdl_amount = fields.Float(
        string="SDL", compute="_compute_l10n_za_totals", store=False
    )
    l10n_za_gross_amount = fields.Float(
        string="Gross", compute="_compute_l10n_za_totals", store=False
    )
    l10n_za_net_amount = fields.Float(
        string="Net", compute="_compute_l10n_za_totals", store=False
    )

    @api.depends("line_ids")
    def _compute_l10n_za_totals(self):
        for slip in self:
            slip.l10n_za_gross_amount = slip.get_salary_line_total("GROSS")
            slip.l10n_za_paye_amount = slip.get_salary_line_total("PAYE")
            slip.l10n_za_uif_amount = slip.get_salary_line_total("UIF_EE")
            slip.l10n_za_sdl_amount = slip.get_salary_line_total("SDL_ER")
            slip.l10n_za_net_amount = slip.get_salary_line_total("NET")

    def _get_tools_dict(self):
        res = super()._get_tools_dict()
        res.update({
            "l10n_za_compute_paye": self._l10n_za_compute_paye,
            "l10n_za_get_parameter": self._l10n_za_get_parameter,
            "l10n_za_get_bracket_tax": self._l10n_za_get_bracket_tax,
        })
        return res

    def _l10n_za_get_parameter(self, code):
        return self.env["hr.rule.parameter"].get_parameter(
            code, date=self.date_from, company_id=self.company_id.id
        )

    def _l10n_za_get_bracket_tax(self, taxable_amount):
        brackets = self.env["hr.rule.parameter.bracket"].get_brackets(
            "l10n_za_paye_brackets",
            date=self.date_from,
            company_id=self.company_id.id,
        )
        for bracket in brackets:
            if bracket.to_amount and taxable_amount > bracket.to_amount:
                continue
            return bracket.base_amount + (taxable_amount * bracket.rate / 100.0)
        return 0.0

    def _l10n_za_compute_paye(self, taxable_amount, rebate_type, medical_credits):
        raw_tax = self._l10n_za_get_bracket_tax(taxable_amount)
        rebate_param = f"l10n_za_rebate_{rebate_type or 'primary'}"
        annual_rebate = self._l10n_za_get_parameter(rebate_param)
        monthly_rebate = annual_rebate / 12.0
        after_rebate = max(raw_tax - monthly_rebate, 0.0)
        main_member_credit = self._l10n_za_get_parameter("l10n_za_medical_credit_main")
        dep_credit = self._l10n_za_get_parameter("l10n_za_medical_credit_dependent")
        total_medical_credits = main_member_credit + (dep_credit * medical_credits)
        return max(after_rebate - total_medical_credits, 0.0)

    def get_salary_line_total(self, code):
        line = self.line_ids.filtered(lambda l: l.code == code)
        return abs(line.total) if line else 0.0

    def l10n_za_get_leave_days(self):
        self.ensure_one()
        if not self.employee_id:
            return 0.0
        allocation = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),
            ('holiday_status_id.time_type', '=', 'leave'),
        ], order='date_from desc', limit=1)
        if allocation:
            return allocation.number_of_days - allocation.leaves_count
        return 0.0

    def l10n_za_get_ytd(self, code):
        self.ensure_one()
        slips = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'done'),
            ('date_from', '>=', date(self.date_from.year, 1, 1)),
            ('id', '<=', self.id),
        ])
        total = 0.0
        for slip in slips:
            total += slip.get_salary_line_total(code)
        return total

    def l10n_za_get_company_contributions(self):
        self.ensure_one()
        return self.line_ids.filtered(lambda l: l.category_id.code in ('EMPLOYER_COST',) and l.appears_on_payslip)
