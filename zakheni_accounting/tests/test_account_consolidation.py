from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestConsolidationFunctional(TransactionCase):
    """Functional tests for multi-company account consolidation."""

    def setUp(self):
        super().setUp()
        self.Consolidation = self.env['zakheni.account.consolidation']
        self.ConsolidationLine = self.env['zakheni.account.consolidation.line']
        self.Account = self.env['account.account']
        self.Move = self.env['account.move']
        self.Partner = self.env['res.partner']
        self.Company = self.env['res.company']
        self.main_company = self.env.company

    def _create_company(self, name):
        return self.Company.create({
            'name': name,
            'currency_id': self.main_company.currency_id.id,
        })

    def _create_invoice(self, company, partner, amount=1000):
        inv = self.Move.with_company(company).create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'company_id': company.id,
            'invoice_date': fields.Date.today(),
            'invoice_date_due': fields.Date.today() + timedelta(days=30),
            'invoice_line_ids': [(0, 0, {
                'name': 'Consol line',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        inv.with_company(company).action_post()
        return inv

    def test_consolidation_lifecycle(self):
        """Create, compute lines, verify state and line creation."""
        company_b = self._create_company('Subsidiary B')
        partner = self.Partner.create({'name': 'Consol', 'customer_rank': 1})

        self._create_invoice(self.main_company, partner, amount=50000)
        self._create_invoice(company_b, partner, amount=30000)

        cons = self.Consolidation.create({
            'name': 'Monthly Consolidation',
            'date': fields.Date.today(),
            'company_ids': [(4, self.main_company.id), (4, company_b.id)],
            'target_company_id': self.main_company.id,
        })
        self.assertEqual(cons.state, 'draft')

        cons.action_compute()
        self.assertGreaterEqual(len(cons.line_ids), 1,
                                'At least one consolidation line expected')

    def test_consolidation_aggregates_balances(self):
        """Balances from selected companies should be combined."""
        company_b = self._create_company('Sub C')
        partner = self.Partner.create({'name': 'Agg', 'customer_rank': 1})

        self._create_invoice(self.main_company, partner, amount=100000)
        self._create_invoice(company_b, partner, amount=75000)

        cons = self.Consolidation.create({
            'name': 'Agg Test',
            'date': fields.Date.today(),
            'company_ids': [(4, self.main_company.id), (4, company_b.id)],
            'target_company_id': self.main_company.id,
        })
        cons.action_compute()

        for line in cons.line_ids:
            if abs(line.balance) > 0:
                self.assertGreaterEqual(abs(line.balance), 25000)

    def test_consolidation_excludes_unselected_companies(self):
        """Companies not selected should be absent from lines."""
        company_b = self._create_company('Sub B')
        company_c = self._create_company('Sub C')
        partner = self.Partner.create({'name': 'Excl', 'customer_rank': 1})

        self._create_invoice(self.main_company, partner, amount=40000)
        self._create_invoice(company_b, partner, amount=30000)
        self._create_invoice(company_c, partner, amount=20000)

        cons = self.Consolidation.create({
            'name': 'Excl Test',
            'date': fields.Date.today(),
            'company_ids': [(4, self.main_company.id), (4, company_b.id)],
            'target_company_id': self.main_company.id,
        })
        cons.action_compute()

        source_companies = cons.line_ids.mapped('source_company_id')
        self.assertIn(self.main_company, source_companies)
        self.assertIn(company_b, source_companies)
        self.assertNotIn(company_c, source_companies)

    def test_consolidation_line_maps_source_to_target(self):
        """Each consolidation line should have source and target accounts."""
        company_b = self._create_company('Sub D')
        partner = self.Partner.create({'name': 'Map', 'customer_rank': 1})

        self._create_invoice(self.main_company, partner, amount=60000)

        cons = self.Consolidation.create({
            'name': 'Map Test',
            'date': fields.Date.today(),
            'company_ids': [(4, self.main_company.id)],
            'target_company_id': self.main_company.id,
        })
        cons.action_compute()

        for line in cons.line_ids:
            self.assertTrue(line.source_company_id,
                            'Source company required')
            self.assertTrue(line.source_account_id,
                            'Source account required')
            self.assertTrue(line.target_account_id,
                            'Target account required')

    def test_consolidation_no_transactions(self):
        """No transactions should yield zero consolidation lines."""
        cons = self.Consolidation.create({
            'name': 'Empty',
            'date': fields.Date.today(),
            'company_ids': [(4, self.main_company.id)],
            'target_company_id': self.main_company.id,
        })
        cons.action_compute()
        self.assertEqual(len(cons.line_ids), 0)

    def test_consolidation_cascade_delete(self):
        """Deleting a consolidation should cascade-delete its lines."""
        b = self._create_company('Sub E')
        p = self.Partner.create({'name': 'C', 'customer_rank': 1})
        self._create_invoice(self.main_company, p, amount=10000)
        cons = self.Consolidation.create({
            'name': 'Cascade',
            'company_ids': [(4, self.main_company.id)],
            'target_company_id': self.main_company.id,
        })
        cons.action_compute()
        line_ids = cons.line_ids.ids
        self.assertTrue(line_ids)
        cons.unlink()
        self.assertEqual(len(self.ConsolidationLine.search([('id', 'in', line_ids)])), 0)

    def test_consolidation_target_company_default(self):
        """target_company_id should default to current company."""
        cons = self.Consolidation.create({
            'name': 'Default',
            'company_ids': [(4, self.main_company.id)],
        })
        self.assertEqual(cons.target_company_id.id, self.main_company.id)

    def test_consolidation_date_default(self):
        """Date should default to today."""
        cons = self.Consolidation.create({
            'name': 'Date Default',
            'company_ids': [(4, self.main_company.id)],
        })
        self.assertEqual(cons.date, fields.Date.today())
