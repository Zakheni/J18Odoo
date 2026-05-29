from odoo import api, models


class ReportL10nZaEmp201(models.AbstractModel):
    _name = "report.l10n_za_hr_payroll.report_emp201"
    _description = "SARS EMP201 Monthly Return Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["l10n_za.emp201.wizard"].browse(
            data.get("wizard_id")
        )
        emp201_data = docs._get_emp201_lines()
        return {
            "doc_ids": docids,
            "doc_model": "l10n_za.emp201.wizard",
            "docs": docs,
            "data": data,
            "emp201_data": emp201_data,
        }
