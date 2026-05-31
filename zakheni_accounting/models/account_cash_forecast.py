from odoo import api, fields, models


class AccountCashForecast(models.Model):
    _name = 'zakheni.cash.forecast'
    _description = 'Cash Flow Forecast'
    _order = 'date, id'

    date = fields.Date('Date', required=True)
    name = fields.Char('Description')
    company_id = fields.Many2one('res.company', 'Company',
        default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', 'Currency',
        default=lambda self: self.env.company.currency_id)
    inflow = fields.Monetary('Expected Inflow', currency_field='currency_id')
    outflow = fields.Monetary('Expected Outflow', currency_field='currency_id')
    balance = fields.Monetary('Expected Balance', currency_field='currency_id',
        compute='_compute_balance', store=True)
    move_id = fields.Many2one('account.move', 'Source Move',
        help='The invoice/bill this forecast line is based on.')
    forecast_type = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('bill', 'Vendor Bill'),
        ('payroll', 'Payroll'),
        ('recurring', 'Recurring'),
        ('manual', 'Manual Entry'),
    ], string='Type', default='manual')

    @api.depends('inflow', 'outflow')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.inflow - rec.outflow

    @api.model
    def generate_forecast(self, days=90):
        self.search([('company_id', '=', self.env.company.id)]).unlink()
        today = fields.Date.today()
        from datetime import timedelta
        horizon = today + timedelta(days=days)

        domain = [
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy')),
            ('company_id', '=', self.env.company.id),
            ('invoice_date_due', '>=', today),
            ('invoice_date_due', '<=', horizon),
        ]
        invoices = self.env['account.move'].search(domain + [('move_type', 'in', ('out_invoice',))])
        bills = self.env['account.move'].search(domain + [('move_type', 'in', ('in_invoice',))])

        lines = []
        for inv in invoices:
            lines.append({
                'date': inv.invoice_date_due,
                'name': inv.name or inv.display_name,
                'inflow': inv.amount_residual,
                'move_id': inv.id,
                'forecast_type': 'invoice',
                'company_id': inv.company_id.id,
            })
        for bill in bills:
            lines.append({
                'date': bill.invoice_date_due,
                'name': bill.name or bill.display_name,
                'outflow': bill.amount_residual,
                'move_id': bill.id,
                'forecast_type': 'bill',
                'company_id': bill.company_id.id,
            })
        if lines:
            self.create(lines)
        return True
