from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestCashForecastFunctional(TransactionCase):
    """Functional tests for cash flow forecasting generation and auto-creation."""

    def setUp(self):
        super().setUp()
        self.Forecast = self.env['zakheni.cash.forecast']
        self.Move = self.env['account.move']
        self.Partner = self.env['res.partner']
        self.company = self.env.company

    def _create_invoice(self, partner, amount=1000, due_in_days=30,
                        move_type='out_invoice', post=True):
        inv = self.Move.create({
            'move_type': move_type,
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=due_in_days),
            'invoice_line_ids': [(0, 0, {
                'name': 'Forecast test',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        if post:
            inv.action_post()
        return inv

    def test_generate_forecast_creates_inflow_and_outflow_lines(self):
        """generate_forecast() should create inflow for invoices, outflow for bills."""
        partner = self.Partner.create({'name': 'Cust', 'customer_rank': 1})
        vendor = self.Partner.create({'name': 'Vendor', 'supplier_rank': 1})

        self._create_invoice(partner, amount=50000, due_in_days=15)
        self._create_invoice(partner, amount=30000, due_in_days=30)
        self._create_invoice(vendor, amount=20000, due_in_days=20, move_type='in_invoice')
        self._create_invoice(vendor, amount=15000, due_in_days=35, move_type='in_invoice')

        self.Forecast.generate_forecast(days=90)

        inflow = self.Forecast.search([
            ('forecast_type', '=', 'invoice'),
            ('company_id', '=', self.company.id),
        ])
        outflow = self.Forecast.search([
            ('forecast_type', '=', 'bill'),
            ('company_id', '=', self.company.id),
        ])

        self.assertEqual(len(inflow), 2)
        self.assertEqual(len(outflow), 2)
        self.assertAlmostEqual(sum(inflow.mapped('inflow')), 80000, delta=0.01)
        self.assertAlmostEqual(sum(outflow.mapped('outflow')), 35000, delta=0.01)

    def test_forecast_excludes_paid_invoices(self):
        """Paid invoices should not appear in the forecast."""
        partner = self.Partner.create({'name': 'Paid', 'customer_rank': 1})
        unpaid = self._create_invoice(partner, amount=15000, due_in_days=30)
        paid = self._create_invoice(partner, amount=5000, due_in_days=10)

        paid._compute_payment_state()
        paid.write({'payment_state': 'paid'})

        self.Forecast.generate_forecast(days=90)

        self.assertEqual(len(self.Forecast.search([('move_id', '=', unpaid.id)])), 1)
        self.assertEqual(len(self.Forecast.search([('move_id', '=', paid.id)])), 0)

    def test_forecast_horizon_excludes_far_future(self):
        """Invoices due beyond the horizon should be excluded."""
        partner = self.Partner.create({'name': 'Horizon', 'customer_rank': 1})
        self._create_invoice(partner, amount=10000, due_in_days=30)
        self._create_invoice(partner, amount=20000, due_in_days=180)

        self.Forecast.generate_forecast(days=60)

        lines = self.Forecast.search([('company_id', '=', self.company.id)])
        self.assertEqual(len(lines), 1)
        self.assertAlmostEqual(lines.inflow, 10000, delta=0.01)

    def test_forecast_regeneration_clears_stale_lines(self):
        """Regenerating the forecast should clear old lines first."""
        partner = self.Partner.create({'name': 'Fresh', 'customer_rank': 1})

        self.Forecast.create({
            'date': fields.Date.today(),
            'name': 'Stale manual line',
            'inflow': 99999,
            'forecast_type': 'manual',
        })

        self._create_invoice(partner, amount=25000, due_in_days=15)
        self.Forecast.generate_forecast(days=90)

        stale = self.Forecast.search([('name', '=', 'Stale manual line')])
        self.assertEqual(len(stale), 0)

    def test_auto_create_forecast_on_invoice_post(self):
        """Posting an invoice should auto-create a cash flow line via action_post()."""
        partner = self.Partner.create({'name': 'Auto CF', 'customer_rank': 1})
        inv = self._create_invoice(partner, amount=35000, due_in_days=30)

        self.assertTrue(inv.cash_flow_line_id,
                        'Posted invoice should auto-create forecast line')
        self.assertAlmostEqual(inv.cash_flow_line_id.inflow, 35000, delta=0.01)
        self.assertEqual(inv.cash_flow_line_id.forecast_type, 'invoice')

    def test_auto_create_forecast_on_bill_post(self):
        """Posting a vendor bill should auto-create an outflow forecast line."""
        vendor = self.Partner.create({'name': 'Auto V', 'supplier_rank': 1})
        bill = self._create_invoice(vendor, amount=22000, due_in_days=30,
                                     move_type='in_invoice')
        self.assertTrue(bill.cash_flow_line_id)
        self.assertAlmostEqual(bill.cash_flow_line_id.outflow, 22000, delta=0.01)
        self.assertEqual(bill.cash_flow_line_id.forecast_type, 'bill')

    def test_balance_computed_field(self):
        """balance should be stored computed as inflow - outflow."""
        line = self.Forecast.create({
            'date': fields.Date.today(),
            'name': 'Net test',
            'inflow': 100000,
            'outflow': 65000,
            'forecast_type': 'manual',
        })
        self.assertAlmostEqual(line.balance, 35000, delta=0.01)

    def test_draft_invoices_excluded_from_forecast(self):
        """Draft (unposted) invoices should not generate forecast lines."""
        partner = self.Partner.create({'name': 'Draft', 'customer_rank': 1})
        self._create_invoice(partner, amount=12000, due_in_days=20, post=False)

        self.Forecast.generate_forecast(days=90)

        lines = self.Forecast.search([('company_id', '=', self.company.id)])
        self.assertEqual(len(lines), 0)

    def test_forecast_no_transactions(self):
        """Forecast generation with no transactions should produce zero lines."""
        self.Forecast.generate_forecast(days=90)
        self.assertEqual(
            len(self.Forecast.search([('company_id', '=', self.company.id)])), 0)

    def test_forecast_line_type_selection(self):
        """Forecast line should have the correct type selection."""
        partner = self.Partner.create({'name': 'Type', 'customer_rank': 1})
        inv = self._create_invoice(partner, amount=5000, due_in_days=30)
        self.assertEqual(inv.cash_flow_line_id.forecast_type, 'invoice')
        self.assertIn(inv.cash_flow_line_id.forecast_type,
                      ['invoice', 'bill', 'payroll', 'recurring', 'manual'])
