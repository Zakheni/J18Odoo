from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    cash_flow_line_id = fields.Many2one('zakheni.cash.forecast', string='Cash Flow Forecast Line')

    def action_post(self):
        res = super().action_post()
        for move in self:
            if move.move_type in ('out_invoice',) and move.amount_residual > 0:
                forecast = self.env['zakheni.cash.forecast'].create({
                    'date': move.invoice_date_due or move.date,
                    'name': move.name or move.display_name,
                    'inflow': move.amount_residual,
                    'move_id': move.id,
                    'forecast_type': 'invoice',
                    'company_id': move.company_id.id,
                })
                move.cash_flow_line_id = forecast
            elif move.move_type in ('in_invoice',) and move.amount_residual > 0:
                forecast = self.env['zakheni.cash.forecast'].create({
                    'date': move.invoice_date_due or move.date,
                    'name': move.name or move.display_name,
                    'outflow': move.amount_residual,
                    'move_id': move.id,
                    'forecast_type': 'bill',
                    'company_id': move.company_id.id,
                })
                move.cash_flow_line_id = forecast
        return res

    def action_send_followup_manually(self):
        return self.action_send_followup()

    @api.model
    def _cron_auto_followup(self):
        enabled = self.env['ir.config_parameter'].sudo().get_param(
            'zakheni_accounting.enable_auto_followup', 'True')
        if enabled != 'True':
            return
        today = fields.Date.today()
        domain = [
            ('move_type', 'in', ('out_invoice',)),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy')),
            ('partner_id.followup_plan_id', '!=', False),
            ('invoice_date_due', '<=', today),
        ]
        overdue = self.search(domain)
        for move in overdue:
            try:
                move.action_send_followup()
            except Exception:
                continue
