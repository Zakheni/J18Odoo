import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pastel_account_code = fields.Char(string='Pastel Account Code', copy=False)
    pastel_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], string='Pastel Sync Status', default='not_synced', readonly=True)
    last_pastel_sync_date = fields.Datetime(string='Last Pastel Sync', readonly=True)

    def action_sync_to_pastel(self):
        self._sync_partner_to_pastel()
        return self._show_sync_result('Partner synced to Pastel successfully.')

    def action_sync_from_pastel(self):
        self._sync_partner_from_pastel()
        return self._show_sync_result('Partner synced from Pastel successfully.')

    def _sync_partner_to_pastel(self):
        self.ensure_one()
        engine = self.env['pastel.sync.engine']
        try:
            data = engine._map_odoo_partner_to_pastel(self)
            existing = engine.fetch_pastel_debtor(data['AccountCode'])
            if existing:
                engine.update_pastel_debtor(data['AccountCode'], data)
            else:
                engine.create_pastel_debtor(data)
            self.write({
                'pastel_sync_status': 'synced',
                'last_pastel_sync_date': fields.Datetime.now(),
                'pastel_account_code': data['AccountCode'],
            })
        except Exception as e:
            self.pastel_sync_status = 'error'
            raise

    def _sync_partner_from_pastel(self):
        self.ensure_one()
        engine = self.env['pastel.sync.engine']
        ref = self.ref or str(self.id)
        debtor = engine.fetch_pastel_debtor(ref[:15].upper())
        if not debtor:
            debtor = engine.fetch_pastel_debtor_by_vat(self.vat)
        if not debtor:
            raise UserError(_('No matching debtor found in Pastel.'))
        data = engine._map_pastel_debtor_to_odoo(debtor)
        self.write(data)
        self.write({
            'pastel_sync_status': 'synced',
            'last_pastel_sync_date': fields.Datetime.now(),
            'pastel_account_code': debtor['AccountCode'],
        })

    def _show_sync_result(self, message):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sync Result'),
            'res_model': 'pastel.sync.log',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_scope': 'partners',
                'default_direction': 'odoo-to-pastel',
                'default_output': message,
                'default_return_code': 0,
                'default_state': 'success',
            },
        }
