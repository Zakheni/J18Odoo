from odoo import models


class AssetReport(models.AbstractModel):
    _name = 'report.zakheni_asset_management.asset_register'
    _description = 'Asset Register Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['asset.asset'].browse(docids) if docids else self.env['asset.asset'].search([])
        return {
            'doc_ids': docids or docs.ids,
            'doc_model': 'asset.asset',
            'docs': docs,
            'company': self.env.company,
        }
