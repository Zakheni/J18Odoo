import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class PastelSyncWizard(models.TransientModel):
    _name = 'pastel.sync.wizard'
    _description = 'Pastel Sync Wizard'

    sync_direction = fields.Selection([
        ('odoo-to-pastel', 'Odoo \u2192 Pastel'),
        ('pastel-to-odoo', 'Pastel \u2192 Odoo'),
        ('bidirectional', 'Bidirectional'),
    ], string='Direction', default='bidirectional', required=True)
    sync_scope = fields.Selection([
        ('all', 'All (Partners + Products + Invoices)'),
        ('partners', 'Partners Only'),
        ('products', 'Products Only'),
        ('invoices', 'Invoices Only'),
    ], string='Scope', default='all', required=True)

    def action_run_sync(self):
        self.ensure_one()
        engine = self.env['pastel.sync.engine']
        output = engine.run_full_sync(
            direction=self.sync_direction,
            scope=self.sync_scope,
        )
        log = self.env['pastel.sync.log'].create({
            'scope': self.sync_scope,
            'direction': self.sync_direction,
            'output': output,
            'return_code': 0,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sync Result'),
            'res_model': 'pastel.sync.log',
            'view_mode': 'form',
            'res_id': log.id,
            'target': 'new',
        }


class PastelSyncLog(models.Model):
    _name = 'pastel.sync.log'
    _description = 'Pastel Sync Log'
    _order = 'create_date desc'

    scope = fields.Selection([
        ('all', 'All'),
        ('partners', 'Partners'),
        ('products', 'Products'),
        ('invoices', 'Invoices'),
    ], string='Scope', required=True)
    direction = fields.Selection([
        ('odoo-to-pastel', 'Odoo \u2192 Pastel'),
        ('pastel-to-odoo', 'Pastel \u2192 Odoo'),
        ('bidirectional', 'Bidirectional'),
    ], string='Direction', required=True)
    return_code = fields.Integer(string='Return Code', default=0)
    output = fields.Text(string='Output')
    state = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
    ], string='State', compute='_compute_state', store=True)

    def _compute_state(self):
        for r in self:
            r.state = 'success' if r.return_code == 0 else 'error'
