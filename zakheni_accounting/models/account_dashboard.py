from odoo import api, fields, models


class AccountDashboard(models.Model):
    _name = 'zakheni.account.dashboard'
    _description = 'Zakheni Accounting Dashboard'

    bank_count = fields.Integer('Bank Accounts')
    bank_balance = fields.Float('Total Bank Balance', digits=0)
    draft_invoices_count = fields.Integer('Draft Invoices')
    overdue_invoices_count = fields.Integer('Overdue Invoices')
    overdue_amount = fields.Float('Overdue Amount', digits=0)
    unreconciled_count = fields.Integer('Unreconciled Items')
    pending_statements = fields.Integer('Pending Statements')
    cash_flow_forecast = fields.Float('Cash Flow Forecast', digits=0)
    receivables_total = fields.Float('Total Receivables', digits=0)
    payables_total = fields.Float('Total Payables', digits=0)

    def compute_data(self):
        Account = self.env['account.account']
        MoveLine = self.env['account.move.line']
        company = self.env.company

        bank_journals = self.env['account.journal'].search([
            ('type', 'in', ['bank', 'cash']),
            ('company_id', '=', company.id),
        ])
        bank_accounts = bank_journals.mapped('default_account_id')
        bank_balance = 0
        if bank_accounts:
            bank_balance = sum(
                MoveLine.with_context(date_to=False)
                .read_group(
                    [('account_id', 'in', bank_accounts.ids),
                     ('company_id', '=', company.id),
                     ('parent_state', '=', 'posted')],
                    ['balance:sum'],
                    [],
                )[0]['balance:sum'] or 0
                for _ in [1]
            )

        draft_invoices = self.env['account.move'].search_count([
            ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')),
            ('state', '=', 'draft'),
            ('company_id', '=', company.id),
        ])

        today = fields.Date.today()
        overdue_moves = self.env['account.move'].search([
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted'),
            ('invoice_date_due', '<', today),
            ('company_id', '=', company.id),
            ('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy')),
        ])
        overdue_amount = sum(overdue_moves.mapped('amount_residual'))

        receivable_accounts = Account.search([
            ('account_type', '=', 'asset_receivable'),
            ('company_id', '=', company.id),
        ])
        payables = Account.search([
            ('account_type', '=', 'liability_payable'),
            ('company_id', '=', company.id),
        ])

        def account_balance(accounts):
            if not accounts:
                return 0
            result = MoveLine.read_group(
                [('account_id', 'in', accounts.ids),
                 ('company_id', '=', company.id),
                 ('parent_state', '=', 'posted')],
                ['balance:sum'],
                [],
            )
            return result[0]['balance:sum'] or 0

        receivables_total = account_balance(receivable_accounts)
        payables_total = account_balance(payables)

        statements = self.env['account.bank.statement'].search_count([
            ('state', '=', 'open'),
            ('company_id', '=', company.id),
        ])

        pending_invoices = self.env['account.move'].search([
            ('move_type', 'in', ('out_invoice', 'out_refund')),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy')),
            ('company_id', '=', company.id),
        ])
        pending_bills = self.env['account.move'].search([
            ('move_type', 'in', ('in_invoice', 'in_refund')),
            ('state', '=', 'posted'),
            ('payment_state', 'not in', ('paid', 'reversed', 'invoicing_legacy')),
            ('company_id', '=', company.id),
        ])
        cash_flow = sum(pending_invoices.mapped('amount_residual')) - sum(pending_bills.mapped('amount_residual'))

        return {
            'bank_count': len(bank_journals),
            'bank_balance': bank_balance,
            'draft_invoices_count': draft_invoices,
            'overdue_invoices_count': len(overdue_moves),
            'overdue_amount': overdue_amount,
            'unreconciled_count': 0,
            'pending_statements': statements,
            'cash_flow_forecast': cash_flow,
            'receivables_total': receivables_total,
            'payables_total': payables_total,
        }
