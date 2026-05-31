from odoo import api, fields, models


class AccountConsolidation(models.Model):
    _name = 'zakheni.account.consolidation'
    _description = 'Account Consolidation'
    _order = 'date desc, id'

    name = fields.Char('Consolidation Name', required=True)
    date = fields.Date('Date', required=True, default=fields.Date.today)
    company_ids = fields.Many2many('res.company', string='Companies to Consolidate',
        required=True)
    target_company_id = fields.Many2one('res.company', string='Target Company',
        default=lambda self: self.env.company, required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], string='Status', default='draft')
    line_ids = fields.One2many('zakheni.account.consolidation.line', 'consolidation_id',
        string='Lines')

    def action_compute(self):
        self.ensure_one()
        self.line_ids.unlink()
        Account = self.env['account.account']
        MoveLine = self.env['account.move.line']
        lines = []
        accounts = Account.search([('company_id', 'in', self.company_ids.ids)])
        for account in accounts:
            if account.company_id.id not in self.company_ids.ids:
                continue
            target_account = Account.search([
                ('code', '=', account.code),
                ('company_id', '=', self.target_company_id.id),
            ], limit=1)
            if not target_account:
                continue
            balance = MoveLine.read_group([
                ('account_id', '=', account.id),
                ('company_id', '=', account.company_id.id),
                ('parent_state', '=', 'posted'),
            ], ['balance:sum'], [])[0]['balance:sum'] or 0
            if balance:
                lines.append({
                    'consolidation_id': self.id,
                    'source_company_id': account.company_id.id,
                    'source_account_id': account.id,
                    'target_account_id': target_account.id,
                    'balance': balance,
                })
        if lines:
            self.create(lines)


class AccountConsolidationLine(models.Model):
    _name = 'zakheni.account.consolidation.line'
    _description = 'Consolidation Line'

    consolidation_id = fields.Many2one('zakheni.account.consolidation',
        string='Consolidation', ondelete='cascade', required=True)
    source_company_id = fields.Many2one('res.company', string='Source Company')
    source_account_id = fields.Many2one('account.account', string='Source Account')
    target_account_id = fields.Many2one('account.account', string='Target Account',
        required=True)
    balance = fields.Float('Balance', digits=0)
