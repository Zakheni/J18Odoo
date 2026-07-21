import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    pastel_transaction_no = fields.Char(string='Pastel Transaction No', copy=False)
    pastel_sync_status = fields.Selection([
        ('not_synced', 'Not Synced'),
        ('synced', 'Synced'),
        ('error', 'Error'),
    ], string='Pastel Sync Status', default='not_synced', readonly=True)
    last_pastel_sync_date = fields.Datetime(string='Last Pastel Sync', readonly=True)

    def action_sync_invoice_to_pastel(self):
        self.ensure_one()
        engine = self.env['pastel.sync.engine']
        partner = self.partner_id
        if not partner:
            raise UserError(_('Invoice has no partner.'))

        account_code = (partner.ref or str(partner.id))[:15].upper()
        debtor = engine.fetch_pastel_debtor(account_code)
        if not debtor:
            raise UserError(_(
                'Debtor "%s" not found in Pastel. Sync the partner first.'
            ) % account_code)

        header = engine._map_odoo_invoice_to_pastel(self, account_code)
        engine.create_pastel_transaction_header(header)
        for i, line in enumerate(self.invoice_line_ids, 1):
            line_data = engine._map_odoo_line_to_pastel(line, i)
            engine.create_pastel_transaction_line(line_data)

        self.write({
            'pastel_sync_status': 'synced',
            'last_pastel_sync_date': fields.Datetime.now(),
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sync Result'),
            'res_model': 'pastel.sync.log',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_scope': 'invoices',
                'default_direction': 'odoo-to-pastel',
                'default_output': _('Invoice %s synced to Pastel successfully.') % self.name,
                'default_return_code': 0,
                'default_state': 'success',
            },
        }
