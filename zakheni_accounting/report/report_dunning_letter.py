from odoo import api, models


class ReportDunningLetter(models.AbstractModel):
    _name = 'report.zakheni_accounting.dunning_letter'
    _description = 'Dunning Letter Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'company': self.env.company,
        }
