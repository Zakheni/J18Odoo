from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_followup_date = fields.Date('Last Follow-up Date')
    next_followup_date = fields.Date('Next Follow-up Date')
    credit_limit = fields.Float('Credit Limit',
        company_dependent=True, help='Set a credit limit for this customer. 0 = no limit.')
    credit_used = fields.Monetary('Credit Used', compute='_compute_credit_used',
        currency_field='currency_id')
    credit_available = fields.Monetary('Credit Available', compute='_compute_credit_used',
        currency_field='currency_id')
    credit_exceeded = fields.Boolean('Credit Limit Exceeded', compute='_compute_credit_used')

    def _compute_credit_used(self):
        for partner in self:
            total = 0
            if partner.credit_limit > 0:
                invoices = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('move_type', 'in', ('out_invoice', 'out_refund')),
                    ('state', '=', 'posted'),
                    ('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy')),
                ])
                total = sum(invoices.mapped('amount_residual'))
            partner.credit_used = total
            partner.credit_available = max(0, partner.credit_limit - total) if partner.credit_limit > 0 else 0
            partner.credit_exceeded = total > partner.credit_limit if partner.credit_limit > 0 else False
