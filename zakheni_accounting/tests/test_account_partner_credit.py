from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestPartnerCreditFunctional(TransactionCase):
    """Functional tests for partner credit limit tracking."""

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.Move = self.env['account.move']

    def _create_invoice(self, partner, amount=1000, days_overdue=0, state='posted'):
        due = fields.Date.today() - timedelta(days=days_overdue)
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': due,
            'invoice_date_due': due,
            'invoice_line_ids': [(0, 0, {
                'name': 'Credit test',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        if state == 'posted':
            inv.action_post()
        return inv

    def test_credit_limit_basic_workflow(self):
        """Set credit limit, create invoices, verify usage computation."""
        partner = self.Partner.create({
            'name': 'Credit Customer',
            'customer_rank': 1,
            'credit_limit': 50000,
        })
        self.assertEqual(partner.credit_limit, 50000)
        self.assertEqual(partner.credit_used, 0)
        self.assertEqual(partner.credit_available, 50000)
        self.assertFalse(partner.credit_exceeded)

        self._create_invoice(partner, amount=20000)
        self._create_invoice(partner, amount=15000)

        partner._compute_credit_used()
        self.assertAlmostEqual(partner.credit_used, 35000, delta=0.01)
        self.assertAlmostEqual(partner.credit_available, 50000, delta=0.01)
        self.assertFalse(partner.credit_exceeded)

    def test_credit_exceeded_when_over_limit(self):
        """Flag should be True when invoices exceed credit limit."""
        partner = self.Partner.create({
            'name': 'Over',
            'customer_rank': 1,
            'credit_limit': 10000,
        })
        self._create_invoice(partner, amount=12000)
        partner._compute_credit_used()
        self.assertTrue(partner.credit_exceeded)

    def test_credit_at_limit_not_exceeded(self):
        """Exactly at limit should not trigger exceeded flag."""
        partner = self.Partner.create({
            'name': 'At Limit',
            'customer_rank': 1,
            'credit_limit': 25000,
        })
        self._create_invoice(partner, amount=25000)
        partner._compute_credit_used()
        self.assertFalse(partner.credit_exceeded)

    def test_paid_invoices_excluded_from_credit(self):
        """Paid invoices should not count towards credit used."""
        partner = self.Partner.create({
            'name': 'Paid',
            'customer_rank': 1,
            'credit_limit': 30000,
        })
        self._create_invoice(partner, amount=10000)
        paid = self._create_invoice(partner, amount=5000)
        paid._compute_payment_state()
        paid.write({'payment_state': 'paid'})

        partner._compute_credit_used()
        self.assertAlmostEqual(partner.credit_used, 10000, delta=0.01)

    def test_draft_invoices_excluded_from_credit(self):
        """Draft invoices should not count towards credit used."""
        partner = self.Partner.create({
            'name': 'Draft',
            'customer_rank': 1,
            'credit_limit': 50000,
        })
        self._create_invoice(partner, amount=30000, state='draft')
        partner._compute_credit_used()
        self.assertEqual(partner.credit_used, 0)

    def test_zero_limit_disables_tracking(self):
        """Zero credit limit means no tracking (fields stay at defaults)."""
        partner = self.Partner.create({
            'name': 'No Limit',
            'customer_rank': 1,
            'credit_limit': 0,
        })
        self._create_invoice(partner, amount=100000)
        partner._compute_credit_used()
        self.assertEqual(partner.credit_used, 0)
        self.assertFalse(partner.credit_exceeded)

    def test_credit_independent_per_partner(self):
        """Each partner's credit is computed independently."""
        p1 = self.Partner.create({
            'name': 'High', 'customer_rank': 1, 'credit_limit': 100000,
        })
        p2 = self.Partner.create({
            'name': 'Low', 'customer_rank': 1, 'credit_limit': 5000,
        })
        self._create_invoice(p1, amount=80000)
        self._create_invoice(p2, amount=6000)

        (p1 + p2)._compute_credit_used()

        self.assertAlmostEqual(p1.credit_used, 80000, delta=0.01)
        self.assertFalse(p1.credit_exceeded)
        self.assertAlmostEqual(p2.credit_used, 6000, delta=0.01)
        self.assertTrue(p2.credit_exceeded)

    def test_credit_available_not_negative_display(self):
        """credit_available formula uses max(0, ...)."""
        partner = self.Partner.create({
            'name': 'Neg', 'customer_rank': 1, 'credit_limit': 10000,
        })
        self._create_invoice(partner, amount=15000)
        partner._compute_credit_used()
        self.assertGreaterEqual(partner.credit_available, 0)

    def test_followup_date_fields(self):
        """Partner should track last and next follow-up dates."""
        partner = self.Partner.create({
            'name': 'Fup',
            'customer_rank': 1,
            'last_followup_date': fields.Date.today(),
            'next_followup_date': fields.Date.today() + timedelta(days=7),
        })
        self.assertEqual(partner.last_followup_date, fields.Date.today())
        self.assertEqual(partner.next_followup_date,
                         fields.Date.today() + timedelta(days=7))

    def test_followup_responsible(self):
        """Partner should have a follow-up responsible user."""
        user = self.env.ref('base.user_admin')
        partner = self.Partner.create({
            'name': 'Resp',
            'customer_rank': 1,
            'followup_responsible_id': user.id,
        })
        self.assertEqual(partner.followup_responsible_id.id, user.id)
