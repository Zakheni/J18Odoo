from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class L10nZaEmp201Wizard(models.TransientModel):
    _name = "l10n_za.emp201.wizard"
    _description = "SARS EMP201 Monthly Return"

    tax_year = fields.Selection(
        [(str(y), str(y)) for y in range(2024, 2031)],
        string="Tax Year",
        default=str(date.today().year),
        required=True,
    )
    month = fields.Selection(
        [
            ("1", "January"), ("2", "February"), ("3", "March"),
            ("4", "April"), ("5", "May"), ("6", "June"),
            ("7", "July"), ("8", "August"), ("9", "September"),
            ("10", "October"), ("11", "November"), ("12", "December"),
        ],
        string="Month",
        required=True,
        default=str(date.today().month),
    )
    date_from = fields.Date(compute="_compute_dates", store=False)
    date_to = fields.Date(compute="_compute_dates", store=False)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.depends("tax_year", "month")
    def _compute_dates(self):
        for rec in self:
            year = int(rec.tax_year)
            m = int(rec.month)
            rec.date_from = date(year, m, 1)
            rec.date_to = date(year, m, 1) + relativedelta(months=1, days=-1)

    def action_print_emp201(self):
        data = {
            "wizard_id": self.id,
            "company_id": self.company_id.id,
            "date_from": self.date_from.isoformat(),
            "date_to": self.date_to.isoformat(),
            "tax_year": self.tax_year,
            "month": self.month,
        }
        return self.env.ref(
            "l10n_za_hr_payroll.action_report_l10n_za_emp201"
        ).report_action(self, data=data)

    def _get_emp201_lines(self):
        self.ensure_one()
        company = self.company_id
        payslips = self.env["hr.payslip"].search([
            ("date_from", ">=", self.date_from),
            ("date_to", "<=", self.date_to),
            ("state", "=", "done"),
            ("company_id", "=", company.id),
        ])
        lines = []
        total_paye = 0.0
        total_uif_ee = 0.0
        total_uif_er = 0.0
        total_sdl_er = 0.0
        total_gross = 0.0
        for slip in payslips:
            gross = slip.get_salary_line_total("GROSS")
            paye = slip.get_salary_line_total("PAYE")
            uif_ee = slip.get_salary_line_total("UIF_EE")
            uif_er = slip.get_salary_line_total("UIF_ER")
            sdl_er = slip.get_salary_line_total("SDL_ER")
            line_data = {
                "employee": slip.employee_id.name,
                "id_number": slip.employee_id.l10n_za_id_number or "",
                "tax_number": slip.employee_id.l10n_za_tax_number or "",
                "gross": gross,
                "paye": paye,
                "uif_ee": uif_ee,
                "uif_er": uif_er,
                "sdl_er": sdl_er,
            }
            lines.append(line_data)
            total_gross += gross
            total_paye += paye
            total_uif_ee += uif_ee
            total_uif_er += uif_er
            total_sdl_er += sdl_er
        return {
            "lines": lines,
            "totals": {
                "total_gross": total_gross,
                "total_paye": total_paye,
                "total_uif_ee": total_uif_ee,
                "total_uif_er": total_uif_er,
                "total_sdl_er": total_sdl_er,
                "total_uif": total_uif_ee + total_uif_er,
            },
            "company": company,
            "period": f"{self.month}/{self.tax_year}",
            "date_from": self.date_from,
            "date_to": self.date_to,
        }
