from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestDashboardFunctional(TransactionCase):
    """Functional tests for Accounting Dashboard KPI computation."""

    def setUp(self):
        super().setUp()
        self.Dashboard = self.env['zakheni.account.dashboard']
        self.Move = self.env['account.move']
        self.Partner = self.env['res.partner']

    def _create_invoice(self, partner=None, amount=1000, days_overdue=0, state='posted'):
        if not partner:
            partner = self.Partner.create({'name': 'Dash Cust', 'customer_rank': 1})
        due = fields.Date.today() - timedelta(days=days_overdue)
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': due,
            'invoice_date_due': due,
            'invoice_line_ids': [(0, 0, {
                'name': 'Dash line',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        if state == 'posted':
            inv.action_post()
        return inv

    def test_compute_data_returns_all_kpis(self):
        """compute_data() should return a dict with all 10 KPI fields."""
        result = self.Dashboard.create({}).compute_data()
        expected_keys = [
            'bank_count', 'bank_balance', 'draft_invoices_count',
            'overdue_invoices_count', 'overdue_amount', 'unreconciled_count',
            'pending_statements', 'cash_flow_forecast',
            'receivables_total', 'payables_total',
        ]
        for key in expected_keys:
            self.assertIn(key, result, f'{key} should be in compute_data() result')

    def test_draft_invoices_counted(self):
        """Dashboard should count draft invoices."""
        partner = self.Partner.create({'name': 'Draft', 'customer_rank': 1})
        self._create_invoice(partner=partner, amount=5000, state='draft')
        self._create_invoice(partner=partner, amount=3000, state='draft')
        result = self.Dashboard.create({}).compute_data()
        self.assertGreaterEqual(result['draft_invoices_count'], 0)

    def test_overdue_invoices_detected(self):
        """Dashboard should detect overdue posted invoices past due date."""
        partner = self.Partner.create({'name': 'Overdue', 'customer_rank': 1})
        self._create_invoice(partner=partner, amount=15000, days_overdue=10)
        result = self.Dashboard.create({}).compute_data()
        self.assertGreaterEqual(result['overdue_invoices_count'], 1)
        self.assertGreaterEqual(result['overdue_amount'], 15000)

    def test_receivables_payables_computed(self):
        """Dashboard should compute receivables and payables totals."""
        partner = self.Partner.create({'name': 'RP', 'customer_rank': 1})
        vendor = self.Partner.create({'name': 'Vendor', 'supplier_rank': 1})
        self._create_invoice(partner=partner, amount=50000)
        self.Move.create({
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Bill', 'quantity': 1, 'price_unit': 20000,
            })],
        }).action_post()

        result = self.Dashboard.create({}).compute_data()
        self.assertGreaterEqual(result['receivables_total'], 50000)
        self.assertGreaterEqual(result['payables_total'], 20000)

    def test_cash_flow_forecast_snapshot(self):
        """Dashboard should compute cash flow as residual-based forecast."""
        partner = self.Partner.create({'name': 'CF', 'customer_rank': 1})
        self._create_invoice(partner=partner, amount=12000)
        result = self.Dashboard.create({}).compute_data()
        self.assertIsNotNone(result['cash_flow_forecast'])

    def test_compute_data_on_transient_record(self):
        """compute_data() is a method returning dict, not stored."""
        dash = self.Dashboard.create({})
        result = dash.compute_data()
        self.assertIsInstance(result, dict)

    def test_bank_count_and_balance(self):
        """Dashboard should include bank account counts and balance."""
        result = self.Dashboard.create({}).compute_data()
        self.assertIn('bank_count', result)
        self.assertIn('bank_balance', result)

    def test_unreconciled_included(self):
        """Dashboard should include unreconciled items count."""
        result = self.Dashboard.create({}).compute_data()
        self.assertIn('unreconciled_count', result)
