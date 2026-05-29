from datetime import date

from odoo import api, fields, models


class L10nZaIrp5Wizard(models.TransientModel):
    _name = "l10n_za.irp5.wizard"
    _description = "SARS IRP5/IT3(a) Year-End Certificate"

    tax_year = fields.Selection(
        [(str(y), str(y)) for y in range(2024, 2031)],
        string="Tax Year",
        default=str(date.today().year),
        required=True,
    )
    employee_id = fields.Many2one("hr.employee", string="Employee")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    certificate_type = fields.Selection(
        [
            ("irp5", "IRP5 - Income Tax Certificate"),
            ("it3a", "IT3(a) - Interest / Investment Income"),
        ],
        string="Certificate Type",
        default="irp5",
        required=True,
    )

    def action_print_irp5(self):
        data = {
            "wizard_id": self.id,
            "employee_id": self.employee_id.id,
            "company_id": self.company_id.id,
            "tax_year": self.tax_year,
            "certificate_type": self.certificate_type,
        }
        return self.env.ref(
            "l10n_za_hr_payroll.action_report_l10n_za_irp5"
        ).report_action(self, data=data)

    def _get_irp5_data(self):
        self.ensure_one()
        year = int(self.tax_year)
        date_from = date(year - 1, 3, 1)
        date_to = date(year, 2, 28)
        domain = [
            ("state", "=", "done"),
            ("date_from", ">=", date_from),
            ("date_to", "<=", date_to),
            ("company_id", "=", self.company_id.id),
        ]
        if self.employee_id:
            domain.append(("employee_id", "=", self.employee_id.id))
        payslips = self.env["hr.payslip"].search(domain)
        employees_data = {}
        for slip in payslips:
            emp = slip.employee_id
            if emp.id not in employees_data:
                employees_data[emp.id] = {
                    "employee": emp,
                    "gross": 0.0,
                    "basic": 0.0,
                    "allowances": 0.0,
                    "pension_ee": 0.0,
                    "provident_ee": 0.0,
                    "paye": 0.0,
                    "uif_ee": 0.0,
                    "medical": 0.0,
                    "net": 0.0,
                    "payslip_count": 0,
                }
            d = employees_data[emp.id]
            d["gross"] += slip.get_salary_line_total("GROSS")
            d["basic"] += slip.get_salary_line_total("BASIC")
            d["allowances"] += (
                slip.get_salary_line_total("TRAVEL")
                + slip.get_salary_line_total("HOUSING")
                + slip.get_salary_line_total("CAR")
                + slip.get_salary_line_total("OTHER_ALLOW")
            )
            d["pension_ee"] += slip.get_salary_line_total("PENSION_EE")
            d["provident_ee"] += slip.get_salary_line_total("PROVIDENT_EE")
            d["paye"] += slip.get_salary_line_total("PAYE")
            d["uif_ee"] += slip.get_salary_line_total("UIF_EE")
            d["medical"] += slip.get_salary_line_total("MEDICAL")
            d["net"] += slip.get_salary_line_total("NET")
            d["payslip_count"] += 1
        return {
            "employees": list(employees_data.values()),
            "company": self.company_id,
            "tax_year": self.tax_year,
            "date_from": date_from,
            "date_to": date_to,
            "certificate_type": dict(
                self._fields["certificate_type"].selection
            ).get(self.certificate_type),
        }
