import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    pastel_stock_code = fields.Char(string='Pastel Stock Code', copy=False)
    pastel_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], string='Pastel Sync Status', default='not_synced', readonly=True)
    last_pastel_sync_date = fields.Datetime(string='Last Pastel Sync', readonly=True)

    def action_sync_to_pastel(self):
        self.ensure_one()
        engine = self.env['pastel.sync.engine']
        data = engine._map_odoo_product_to_pastel(self)
        existing = engine.fetch_pastel_stock_item(data['StockCode'])
        if existing:
            engine.update_pastel_stock(data['StockCode'], data)
        else:
            engine.create_pastel_stock(data)
        self.write({
            'pastel_sync_status': 'synced',
            'last_pastel_sync_date': fields.Datetime.now(),
            'pastel_stock_code': data['StockCode'],
        })
        return self._show_result('Product synced to Pastel successfully.')

    def action_sync_from_pastel(self):
        self.ensure_one()
        engine = self.env['pastel.sync.engine']
        code = self.default_code or f'P{self.id}'
        item = engine.fetch_pastel_stock_item(code[:30].upper())
        if not item:
            raise UserError(_('No matching stock item found in Pastel.'))
        data = engine._map_pastel_stock_to_odoo(item)
        self.write(data)
        self.write({
            'pastel_sync_status': 'synced',
            'last_pastel_sync_date': fields.Datetime.now(),
            'pastel_stock_code': item['StockCode'],
        })
        return self._show_result('Product synced from Pastel successfully.')

    def _show_result(self, message):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sync Result'),
            'res_model': 'pastel.sync.log',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_scope': 'products',
                'default_output': message,
                'default_return_code': 0,
                'default_state': 'success',
            },
        }
