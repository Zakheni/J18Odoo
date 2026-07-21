from odoo import api, fields, models


class AccountStatementWizard(models.TransientModel):
    _name = 'zakheni.account.statement.wizard'
    _description = 'Customer Statement Wizard'

    partner_ids = fields.Many2many('res.partner', string='Customers',
        domain=[('customer_rank', '>', 0)], required=True)
    date_from = fields.Date(string='From', required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1))
    date_to = fields.Date(string='To', required=True,
        default=lambda self: fields.Date.context_today(self))
    statement_type = fields.Selection([
        ('outstanding', 'Outstanding Invoices Only'),
        ('all', 'All Transactions'),
    ], string='Statement Type', default='outstanding', required=True)
    min_days_overdue = fields.Integer(string='Min Days Overdue',
        help='Show only invoices overdue by at least this many days. 0 = all.')
    include_aging = fields.Boolean(string='Include Aging Summary', default=True)

    def _get_report_data(self):
        return {
            'date_from': self.date_from.isoformat(),
            'date_to': self.date_to.isoformat(),
            'statement_type': self.statement_type,
            'min_days_overdue': self.min_days_overdue,
            'include_aging': self.include_aging,
            'partner_ids': self.partner_ids.ids,
        }

    def action_print(self):
        data = self._get_report_data()
        return self.env.ref('zakheni_accounting.action_report_customer_statement').report_action(self, data=data)

    def action_send(self):
        self.ensure_one()
        for partner in self.partner_ids:
            self._send_statement(partner)
        return {'type': 'ir.actions.act_window_close'}

    def _send_statement(self, partner):
        data = self._get_report_data()
        data['partner_ids'] = [partner.id]
        report = self.env.ref('zakheni_accounting.action_report_customer_statement')
        pdf_content, _ = report.sudo()._render_qweb_pdf(self.ids, data=data)
        filename = f'Statement - {partner.name}.pdf'

        template = self.env.ref('zakheni_accounting.email_template_statement', raise_if_not_found=False)
        if not template:
            template = self.env.ref('account.email_template_edi_invoice', raise_if_not_found=False)
        if template:
            template.sudo().with_context(
                partner_id=partner.id,
                email_to=partner.email,
            ).send_mail(self.id, force_send=True)
