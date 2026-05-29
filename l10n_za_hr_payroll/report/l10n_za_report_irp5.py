from odoo import api, models


class ReportL10nZaIrp5(models.AbstractModel):
    _name = "report.l10n_za_hr_payroll.report_irp5"
    _description = "SARS IRP5/IT3(a) Certificate Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["l10n_za.irp5.wizard"].browse(
            data.get("wizard_id")
        )
        irp5_data = docs._get_irp5_data()
        return {
            "doc_ids": docids,
            "doc_model": "l10n_za.irp5.wizard",
            "docs": docs,
            "data": data,
            "irp5_data": irp5_data,
        }
