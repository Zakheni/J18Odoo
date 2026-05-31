from odoo import fields, models


class AccountSpread(models.Model):
    _inherit = 'account.spread'

    invoice_id = fields.Many2one('account.move', string='Source Invoice')
