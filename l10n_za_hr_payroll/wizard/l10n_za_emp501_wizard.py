from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class L10nZaEmp501Wizard(models.TransientModel):
    _name = "l10n_za.emp501.wizard"
    _description = "SARS EMP501 Bi-Annual Reconciliation"

    tax_year = fields.Selection(
        [(str(y), str(y)) for y in range(2024, 2031)],
        string="Tax Year",
        default=str(date.today().year),
        required=True,
    )
    period = fields.Selection(
        [
            ("first_half", "First Half (Mar - Aug)"),
            ("second_half", "Second Half (Sep - Feb)"),
        ],
        string="Period",
        required=True,
    )
    date_from = fields.Date(compute="_compute_dates", store=False)
    date_to = fields.Date(compute="_compute_dates", store=False)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.depends("tax_year", "period")
    def _compute_dates(self):
        for rec in self:
            year = int(rec.tax_year)
            if rec.period == "first_half":
                rec.date_from = date(year - 1, 3, 1)
                rec.date_to = date(year - 1, 8, 31)
            else:
                rec.date_from = date(year - 1, 9, 1)
                rec.date_to = date(year, 2, 28)

    def action_print_emp501(self):
        data = {
            "wizard_id": self.id,
            "company_id": self.company_id.id,
            "date_from": self.date_from.isoformat(),
            "date_to": self.date_to.isoformat(),
            "tax_year": self.tax_year,
            "period": self.period,
        }
        return self.env.ref(
            "l10n_za_hr_payroll.action_report_l10n_za_emp501"
        ).report_action(self, data=data)

    def _get_emp501_data(self):
        self.ensure_one()
        payslips = self.env["hr.payslip"].search([
            ("date_from", ">=", self.date_from),
            ("date_to", "<=", self.date_to),
            ("state", "=", "done"),
            ("company_id", "=", self.company_id.id),
        ])
        monthly_data = {}
        for slip in payslips:
            key = slip.date_from.strftime("%Y-%m")
            if key not in monthly_data:
                monthly_data[key] = {
                    "month": slip.date_from.strftime("%B %Y"),
                    "employee_count": 0,
                    "gross": 0.0,
                    "paye": 0.0,
                    "uif_ee": 0.0,
                    "uif_er": 0.0,
                    "sdl_er": 0.0,
                }
            d = monthly_data[key]
            d["gross"] += slip.get_salary_line_total("GROSS")
            d["paye"] += slip.get_salary_line_total("PAYE")
            d["uif_ee"] += slip.get_salary_line_total("UIF_EE")
            d["uif_er"] += slip.get_salary_line_total("UIF_ER")
            d["sdl_er"] += slip.get_salary_line_total("SDL_ER")
            d["employee_count"] += 1
        totals = {
            "gross": sum(d["gross"] for d in monthly_data.values()),
            "paye": sum(d["paye"] for d in monthly_data.values()),
            "uif_ee": sum(d["uif_ee"] for d in monthly_data.values()),
            "uif_er": sum(d["uif_er"] for d in monthly_data.values()),
            "sdl_er": sum(d["sdl_er"] for d in monthly_data.values()),
        }
        return {
            "monthly_lines": list(monthly_data.values()),
            "totals": totals,
            "company": self.company_id,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "period_label": "First Half (Mar-Aug)"
            if self.period == "first_half"
            else "Second Half (Sep-Feb)",
        }
