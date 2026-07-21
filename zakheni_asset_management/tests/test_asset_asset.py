from odoo.tests.common import TransactionCase
from odoo import fields


class TestAssetAsset(TransactionCase):
    """Functional tests for asset.asset model."""

    def setUp(self):
        super().setUp()
        self.Asset = self.env['asset.asset']
        self.Category = self.env['asset.category']
        self.Location = self.env['asset.location']

        self.category = self.Category.create({
            'name': 'Test IT Equipment',
            'code': 'TEST-IT',
            'depreciation_method': 'straight_line',
            'depreciation_duration_months': 36,
            'salvage_value_percent': 10.0,
        })
        self.location = self.Location.create({
            'name': 'Test Office',
            'code': 'T-OFF',
        })

    def test_create_asset(self):
        """Create an asset with minimal required fields."""
        asset = self.Asset.create({
            'name': 'Test Laptop',
            'category_id': self.category.id,
            'purchase_value': 30000.0,
            'current_location_id': self.location.id,
        })
        self.assertTrue(asset.id)
        self.assertTrue(asset.code)
        self.assertEqual(asset.status, 'draft')
        self.assertEqual(asset.purchase_date, fields.Date.today())
        self.assertAlmostEqual(asset.salvage_value, 3000.0, delta=0.01)

    def test_asset_code_auto_generated(self):
        """Asset number should be auto-generated from sequence."""
        a1 = self.Asset.create({'name': 'A', 'category_id': self.category.id, 'purchase_value': 1000})
        a2 = self.Asset.create({'name': 'B', 'category_id': self.category.id, 'purchase_value': 2000})
        self.assertNotEqual(a1.code, a2.code)
        self.assertTrue(a1.code.startswith('AST-'))

    def test_display_name(self):
        """Display name should be 'code - name'."""
        asset = self.Asset.create({'name': 'My Asset', 'category_id': self.category.id, 'purchase_value': 5000})
        expected = f'{asset.code} - My Asset'
        self.assertEqual(asset.display_name, expected)

    def test_salvage_value_computed_from_percent(self):
        """Salvage value should be purchase_value * salvage_value_percent / 100."""
        asset = self.Asset.create({
            'name': 'Salvage Test',
            'category_id': self.category.id,
            'purchase_value': 50000.0,
            'salvage_value_percent': 15.0,
        })
        self.assertAlmostEqual(asset.salvage_value, 7500.0, delta=0.01)

    def test_book_value_equals_purchase_initially(self):
        """Book value should equal purchase value when no depreciation exists."""
        asset = self.Asset.create({
            'name': 'Book Value Test',
            'category_id': self.category.id,
            'purchase_value': 100000.0,
        })
        self.assertAlmostEqual(asset.book_value, 100000.0, delta=0.01)
        self.assertEqual(asset.cumulative_depreciation, 0.0)

    def test_onchange_category_sets_defaults(self):
        """Changing category should set depreciation defaults."""
        asset = self.Asset.create({
            'name': 'Onchange Test',
            'category_id': self.category.id,
            'purchase_value': 20000.0,
        })
        self.assertEqual(asset.depreciation_method, self.category.depreciation_method)
        self.assertEqual(asset.depreciation_duration_months, self.category.depreciation_duration_months)
        self.assertEqual(asset.salvage_value_percent, self.category.salvage_value_percent)

    def test_asset_status_lifecycle(self):
        """Asset status should transition through lifecycle stages."""
        asset = self.Asset.create({
            'name': 'Lifecycle Test',
            'category_id': self.category.id,
            'purchase_value': 15000.0,
        })
        self.assertEqual(asset.status, 'draft')

        asset.status = 'in_use'
        self.assertEqual(asset.status, 'in_use')

        asset.status = 'maintenance'
        self.assertEqual(asset.status, 'maintenance')

        asset.status = 'disposed'
        self.assertEqual(asset.status, 'disposed')

    def test_purchase_value_must_be_positive(self):
        """Purchase value should be > 0."""
        with self.assertRaises(Exception):
            self.Asset.create({
                'name': 'Negative',
                'category_id': self.category.id,
                'purchase_value': 0.0,
            })

    def test_currency_defaults_to_company_currency(self):
        """Currency should default to company currency."""
        asset = self.Asset.create({
            'name': 'Currency Test',
            'category_id': self.category.id,
            'purchase_value': 10000.0,
        })
        self.assertEqual(asset.currency_id.id, self.env.company.currency_id.id)
