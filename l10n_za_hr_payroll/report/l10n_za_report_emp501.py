from odoo import api, models


class ReportL10nZaEmp501(models.AbstractModel):
    _name = "report.l10n_za_hr_payroll.report_emp501"
    _description = "SARS EMP501 Bi-Annual Reconciliation Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["l10n_za.emp501.wizard"].browse(
            data.get("wizard_id")
        )
        emp501_data = docs._get_emp501_data()
        return {
            "doc_ids": docids,
            "doc_model": "l10n_za.emp501.wizard",
            "docs": docs,
            "data": data,
            "emp501_data": emp501_data,
        }
