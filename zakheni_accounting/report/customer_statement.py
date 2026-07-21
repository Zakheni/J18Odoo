from odoo import api, fields, models


class ReportCustomerStatement(models.AbstractModel):
    _name = 'report.zakheni_accounting.customer_statement'
    _description = 'Customer Statement Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data:
            data = {}
        partner_ids = data.get('partner_ids', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        statement_type = data.get('statement_type', 'outstanding')
        min_days_overdue = data.get('min_days_overdue', 0)
        include_aging = data.get('include_aging', True)

        partners = self.env['res.partner'].browse(partner_ids)
        lines = []
        for partner in partners:
            partner_lines, aging = self._get_partner_statement(partner, date_from, date_to, statement_type, min_days_overdue)
            lines.append({
                'partner': partner,
                'lines': partner_lines,
                'aging': aging,
                'total_due': sum(l['balance'] for l in partner_lines if l['balance'] > 0),
                'total_paid': abs(sum(l['balance'] for l in partner_lines if l['balance'] < 0)),
                'include_aging': include_aging,
            })

        return {
            'doc_ids': docids,
            'doc_model': 'zakheni.account.statement.wizard',
            'docs': self.env['zakheni.account.statement.wizard'].browse(docids),
            'data': data,
            'statements': lines,
            'company': self.env.company,
        }

    def _get_partner_statement(self, partner, date_from, date_to, statement_type, min_days_overdue=0):
        today = fields.Date.context_today(self)
        domain = [
            ('partner_id', '=', partner.id),
            ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt')),
            ('state', '=', 'posted'),
        ]
        if statement_type == 'outstanding':
            domain += [('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy'))]
        if date_from:
            domain += [('invoice_date', '>=', date_from)]
        if date_to:
            domain += [('invoice_date', '<=', date_to)]

        moves = self.env['account.move'].search(domain, order='invoice_date, name')
        running_balance = 0
        lines = []
        aging = {'current': 0, '1_30': 0, '31_60': 0, '61_90': 0, '90_plus': 0}
        for move in moves:
            sign = -1 if move.move_type == 'out_refund' else 1
            amount = move.amount_total * sign
            paid = move.amount_total - move.amount_residual
            running_balance += amount
            days_overdue = 0
            aging_bucket = 'current'
            if move.invoice_date_due and move.invoice_date_due < today:
                days_overdue = (today - move.invoice_date_due).days
                if days_overdue <= 30:
                    aging_bucket = '1_30'
                elif days_overdue <= 60:
                    aging_bucket = '31_60'
                elif days_overdue <= 90:
                    aging_bucket = '61_90'
                else:
                    aging_bucket = '90_plus'
            if min_days_overdue > 0 and days_overdue < min_days_overdue:
                continue
            line_balance = running_balance
            aging[aging_bucket] += line_balance
            lines.append({
                'date': move.invoice_date,
                'reference': move.name,
                'description': move.invoice_line_ids[:1].name if move.invoice_line_ids else '',
                'due_date': move.invoice_date_due,
                'days_overdue': days_overdue,
                'amount': amount,
                'paid': paid,
                'balance': line_balance,
                'currency': move.currency_id,
            })
        return lines, aging
