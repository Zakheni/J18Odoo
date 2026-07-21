from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestStatementWizardFunctional(TransactionCase):
    """Functional tests for the Customer Statement wizard (transient model)."""

    def setUp(self):
        super().setUp()
        self.Wizard = self.env['zakheni.account.statement.wizard']
        self.Partner = self.env['res.partner']
        self.Move = self.env['account.move']

    def _create_invoice(self, partner, amount=1000, due_days=30, days_ago=0):
        due = fields.Date.today() - timedelta(days=days_ago) + timedelta(days=due_days)
        inv_date = fields.Date.today() - timedelta(days=days_ago)
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': inv_date,
            'invoice_date_due': due,
            'invoice_line_ids': [(0, 0, {
                'name': 'Stmt line',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        inv.action_post()
        return inv

    def test_wizard_defaults(self):
        """Wizard should have sensible defaults."""
        wiz = self.Wizard.create({
            'partner_ids': [(4, self.Partner.create({
                'name': 'Def', 'customer_rank': 1}).id)],
        })
        self.assertEqual(wiz.statement_type, 'outstanding')
        self.assertTrue(wiz.include_aging)

    def test_action_print_returns_report_action(self):
        """action_print() should return a report action for the customer statement."""
        partner = self.Partner.create({
            'name': 'Print Test', 'customer_rank': 1,
        })
        self._create_invoice(partner, amount=15000)
        wiz = self.Wizard.create({
            'partner_ids': [(4, partner.id)],
            'date_from': fields.Date.today() - timedelta(days=60),
            'date_to': fields.Date.today() + timedelta(days=30),
        })
        result = wiz.action_print()
        self.assertIn('type', result)
        self.assertEqual(result['type'], 'ir.actions.report')

    def test_action_send_returns_close_action(self):
        """action_send() should email the statement and return window close."""
        partner = self.Partner.create({
            'name': 'Email Stmt', 'customer_rank': 1,
            'email': 'billing@example.com',
        })
        self._create_invoice(partner, amount=18000)
        wiz = self.Wizard.create({
            'partner_ids': [(4, partner.id)],
            'date_to': fields.Date.today() + timedelta(days=30),
        })
        result = wiz.action_send()
        self.assertIn('type', result)
        self.assertEqual(result['type'], 'ir.actions.act_window_close')

    def test_wizard_with_multiple_partners(self):
        """Wizard should support multiple partners for batch statements."""
        p1 = self.Partner.create({'name': 'A', 'customer_rank': 1})
        p2 = self.Partner.create({'name': 'B', 'customer_rank': 1})
        self._create_invoice(p1, amount=10000)
        self._create_invoice(p2, amount=20000)

        wiz = self.Wizard.create({
            'partner_ids': [(4, p1.id), (4, p2.id)],
            'date_to': fields.Date.today() + timedelta(days=30),
        })
        self.assertEqual(len(wiz.partner_ids), 2)
        result = wiz.action_print()
        self.assertEqual(result['type'], 'ir.actions.report')

    def test_wizard_date_range(self):
        """Wizard should accept custom date range."""
        partner = self.Partner.create({
            'name': 'Date Range', 'customer_rank': 1,
        })
        self._create_invoice(partner, amount=5000, days_ago=15)
        wiz = self.Wizard.create({
            'partner_ids': [(4, partner.id)],
            'date_from': fields.Date.today() - timedelta(days=30),
            'date_to': fields.Date.today(),
        })
        self.assertEqual(wiz.date_from,
                         fields.Date.today() - timedelta(days=30))
        self.assertEqual(wiz.date_to, fields.Date.today())

    def test_wizard_statement_type_outstanding(self):
        """statement_type='outstanding' should only show unpaid invoices."""
        partner = self.Partner.create({
            'name': 'Out Stmt', 'customer_rank': 1,
        })
        self._create_invoice(partner, amount=12000)
        wiz = self.Wizard.create({
            'partner_ids': [(4, partner.id)],
            'statement_type': 'outstanding',
            'date_to': fields.Date.today() + timedelta(days=30),
        })
        data = wiz._get_report_data()
        self.assertEqual(data['statement_type'], 'outstanding')

    def test_wizard_include_aging(self):
        """include_aging flag should be passed to the report."""
        partner = self.Partner.create({
            'name': 'Aging', 'customer_rank': 1,
        })
        self._create_invoice(partner, amount=25000)
        wiz = self.Wizard.create({
            'partner_ids': [(4, partner.id)],
            'include_aging': True,
            'date_to': fields.Date.today() + timedelta(days=30),
        })
        data = wiz._get_report_data()
        self.assertTrue(data['include_aging'])

    def test_wizard_min_days_overdue(self):
        """min_days_overdue filter should be passed to report."""
        partner = self.Partner.create({
            'name': 'Min Overdue', 'customer_rank': 1,
        })
        self._create_invoice(partner, amount=8000, days_ago=10)
        wiz = self.Wizard.create({
            'partner_ids': [(4, partner.id)],
            'min_days_overdue': 5,
            'date_to': fields.Date.today() + timedelta(days=30),
        })
        data = wiz._get_report_data()
        self.assertEqual(data['min_days_overdue'], 5)
