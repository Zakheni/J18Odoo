from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestAccountMoveExtendedFunctional(TransactionCase):
    """Functional tests for account.move extensions: cash_flow_line_id, action_post override."""

    def setUp(self):
        super().setUp()
        self.Move = self.env['account.move']
        self.Partner = self.env['res.partner']
        self.Account = self.env['account.account']

    def _create_partner(self, name='Test', customer=True, supplier=False):
        return self.Partner.create({
            'name': name,
            'customer_rank': 1 if customer else 0,
            'supplier_rank': 1 if supplier else 0,
        })

    def test_customer_invoice_action_post_creates_cash_flow(self):
        """Posting a customer invoice should create a cash flow line via the override."""
        partner = self._create_partner('CashFlow Inv')
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=30),
            'invoice_line_ids': [(0, 0, {
                'name': 'Services',
                'quantity': 1,
                'price_unit': 50000,
            })],
        })

        self.assertFalse(inv.cash_flow_line_id,
                         'No cash flow line before post')
        inv.action_post()
        self.assertTrue(inv.cash_flow_line_id,
                        'Cash flow line should exist after post')
        self.assertAlmostEqual(inv.cash_flow_line_id.inflow, 50000, delta=0.01)
        self.assertEqual(inv.cash_flow_line_id.forecast_type, 'invoice')

    def test_vendor_bill_action_post_creates_cash_flow(self):
        """Posting a vendor bill should create an outflow cash flow line."""
        vendor = self._create_partner('Vendor CF', customer=False, supplier=True)
        bill = self.Move.create({
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=45),
            'invoice_line_ids': [(0, 0, {
                'name': 'Supplies',
                'quantity': 10,
                'price_unit': 2500,
            })],
        })
        bill.action_post()
        self.assertTrue(bill.cash_flow_line_id)
        self.assertAlmostEqual(bill.cash_flow_line_id.outflow, 25000, delta=0.01)
        self.assertEqual(bill.cash_flow_line_id.forecast_type, 'bill')

    def test_customer_invoice_full_workflow(self):
        """Draft → post → cancel workflow for customer invoice."""
        partner = self._create_partner('ABC Corp')
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=30),
            'invoice_line_ids': [(0, 0, {
                'name': 'Consulting',
                'quantity': 10,
                'price_unit': 1500,
            })],
        })
        self.assertEqual(inv.state, 'draft')
        self.assertAlmostEqual(inv.amount_total, 15000, delta=0.01)

        inv.action_post()
        self.assertEqual(inv.state, 'posted')
        self.assertTrue(inv.name)

        inv.button_cancel()
        self.assertEqual(inv.state, 'cancel')

    def test_vendor_bill_workflow(self):
        """Draft → post workflow for vendor bill."""
        vendor = self._create_partner('Supplier', customer=False, supplier=True)
        bill = self.Move.create({
            'move_type': 'in_invoice',
            'partner_id': vendor.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Office supplies',
                'quantity': 25,
                'price_unit': 240,
            })],
        })
        self.assertEqual(bill.state, 'draft')
        self.assertAlmostEqual(bill.amount_total, 6000, delta=0.01)
        bill.action_post()
        self.assertEqual(bill.state, 'posted')

    def test_balanced_journal_entry_posts(self):
        """A journal entry with equal debits and credits should post."""
        partner = self._create_partner()
        move = self.Move.create({
            'move_type': 'entry',
            'partner_id': partner.id,
            'date': fields.Date.today(),
            'line_ids': [
                (0, 0, {
                    'name': 'Debit',
                    'debit': 5000,
                    'credit': 0,
                    'account_id': self.Account.search([
                        ('account_type', '=', 'asset_receivable'),
                        ('company_id', '=', self.env.company.id),
                    ], limit=1).id,
                }),
                (0, 0, {
                    'name': 'Credit',
                    'debit': 0,
                    'credit': 5000,
                    'account_id': self.Account.search([
                        ('account_type', '=', 'income'),
                        ('company_id', '=', self.env.company.id),
                    ], limit=1).id,
                }),
            ],
        })
        move.action_post()
        self.assertEqual(move.state, 'posted')

    def test_unbalanced_entry_raises_error(self):
        """An imbalanced journal entry should fail to post."""
        partner = self._create_partner()
        move = self.Move.create({
            'move_type': 'entry',
            'partner_id': partner.id,
            'date': fields.Date.today(),
            'line_ids': [
                (0, 0, {
                    'name': 'Debit',
                    'debit': 5000,
                    'credit': 0,
                    'account_id': self.Account.search([
                        ('account_type', '=', 'asset_receivable'),
                        ('company_id', '=', self.env.company.id),
                    ], limit=1).id,
                }),
                (0, 0, {
                    'name': 'Credit',
                    'debit': 0,
                    'credit': 3000,
                    'account_id': self.Account.search([
                        ('account_type', '=', 'income'),
                        ('company_id', '=', self.env.company.id),
                    ], limit=1).id,
                }),
            ],
        })
        with self.assertRaises(Exception):
            move.action_post()

    def test_invoice_multi_line_total(self):
        """Invoice with multiple lines should sum correctly."""
        partner = self._create_partner()
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [
                (0, 0, {'name': 'A', 'quantity': 2, 'price_unit': 5000}),
                (0, 0, {'name': 'B', 'quantity': 3, 'price_unit': 2500}),
                (0, 0, {'name': 'C', 'quantity': 1, 'price_unit': 12000}),
            ],
        })
        expected = 2 * 5000 + 3 * 2500 + 1 * 12000
        self.assertAlmostEqual(inv.amount_total, expected, delta=0.01)

    def test_credit_note_has_negative_total(self):
        """A credit note (out_refund) should have negative amount."""
        partner = self._create_partner()
        refund = self.Move.create({
            'move_type': 'out_refund',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Refund',
                'quantity': 1,
                'price_unit': -5000,
            })],
        })
        refund.action_post()
        self.assertAlmostEqual(refund.amount_total, -5000, delta=0.01)

    def test_followup_fields_on_invoice(self):
        """Invoice should have followup_plan_id via partner."""
        plan = self.env['zakheni.followup.plan'].create({
            'name': 'Test Plan', 'sequence': 1,
        })
        partner = self._create_partner('Fup')
        partner.write({'followup_plan_id': plan.id})
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [(0, 0, {
                'name': 'Fup test', 'quantity': 1, 'price_unit': 1000,
            })],
        })
        inv.action_post()
        self.assertEqual(inv.followup_plan_id.id, plan.id)
        self.assertFalse(inv.followup_level_id)
