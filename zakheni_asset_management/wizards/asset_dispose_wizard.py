from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AssetDisposeWizard(models.TransientModel):
    _name = 'asset.dispose.wizard'
    _description = 'Dispose Asset Wizard'

    asset_id = fields.Many2one('asset.asset', string='Asset', required=True)
    disposal_date = fields.Date(string='Disposal Date', default=fields.Date.today, required=True)
    disposal_type = fields.Selection([
        ('sold', 'Sold'),
        ('scrapped', 'Scrapped'),
        ('donated', 'Donated'),
        ('lost', 'Lost / Stolen'),
        ('retired', 'Retired'),
    ], string='Disposal Type', default='retired', required=True)
    disposal_value = fields.Monetary(string='Proceeds / Sale Value', currency_field='currency_id')
    currency_id = fields.Many2one(related='asset_id.currency_id', string='Currency', readonly=True)
    notes = fields.Text(string='Notes')

    def action_dispose(self):
        self.ensure_one()
        asset = self.asset_id
        if asset.status == 'disposed':
            raise ValidationError('Asset is already disposed.')

        asset.write({
            'status': 'disposed',
            'notes': (asset.notes or '') + f'\n\nDisposed: {self.disposal_date} ({self.disposal_type}). {self.notes or ""}',
        })
        return {'type': 'ir.actions.act_window_close'}
