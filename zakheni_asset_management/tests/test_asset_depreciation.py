from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class TestAssetDepreciation(TransactionCase):
    """Functional tests for depreciation calculation."""

    def setUp(self):
        super().setUp()
        self.Asset = self.env['asset.asset']
        self.DepLine = self.env['asset.depreciation.line']
        self.Wizard = self.env['asset.depreciation.wizard']
        self.Category = self.env['asset.category']

        self.category = self.Category.create({
            'name': 'Depr Cat',
            'depreciation_method': 'straight_line',
            'depreciation_duration_months': 12,
            'salvage_value_percent': 0.0,
        })

    def _create_asset(self, method='straight_line', months=12, value=12000):
        return self.Asset.create({
            'name': 'Depr Asset',
            'category_id': self.category.id,
            'purchase_value': value,
            'depreciation_method': method,
            'depreciation_duration_months': months,
            'salvage_value': 0.0,
        })

    def test_straight_line_monthly_amount(self):
        """Straight line: monthly = (purchase - salvage) / months."""
        asset = self._create_asset(value=12000)
        depr_base = asset.purchase_value - asset.salvage_value
        monthly = depr_base / asset.depreciation_duration_months
        self.assertAlmostEqual(monthly, 1000.0, delta=0.01)

    def test_generate_depreciation_lines(self):
        """Generate depreciation lines for 12 months."""
        asset = self._create_asset(value=12000)
        today = fields.Date.today()

        wiz = self.Wizard.create({
            'asset_id': asset.id,
            'date_from': today,
            'date_to': today + relativedelta(months=11),
            'force_regenerate': True,
        })
        wiz.action_generate()

        lines = asset.depreciation_line_ids
        self.assertEqual(len(lines), 12,
                         'Should generate 12 monthly depreciation lines')
        for line in lines:
            self.assertAlmostEqual(line.amount, 1000.0, delta=0.01)

    def test_depreciation_cumulative_computed(self):
        """Cumulative amount should increase with each line."""
        asset = self._create_asset(value=12000)
        today = fields.Date.today()

        # Create first 3 months manually
        for i in range(3):
            self.DepLine.create({
                'asset_id': asset.id,
                'date': today + relativedelta(months=i),
                'amount': 1000.0,
            })

        lines = asset.depreciation_line_ids.sorted('date')
        for i, line in enumerate(lines):
            self.assertAlmostEqual(line.cumulative_amount, 1000.0 * (i + 1), delta=0.01,
                                   msg=f'Cumulative at month {i+1} should be {1000 * (i+1)}')

    def test_depreciation_updates_book_value(self):
        """Book value should decrease as depreciation is recorded."""
        asset = self._create_asset(value=12000)
        today = fields.Date.today()

        self.DepLine.create({
            'asset_id': asset.id,
            'date': today,
            'amount': 3000.0,
        })

        asset._compute_book_value()
        self.assertAlmostEqual(asset.cumulative_depreciation, 3000.0, delta=0.01)
        self.assertAlmostEqual(asset.book_value, 9000.0, delta=0.01)

    def test_full_depreciation_reaches_salvage(self):
        """Full depreciation should reduce book value to salvage value."""
        asset = self.Asset.create({
            'name': 'Full Depr',
            'category_id': self.category.id,
            'purchase_value': 10000.0,
            'salvage_value': 1000.0,
            'depreciation_duration_months': 9,
        })

        monthly = (10000.0 - 1000.0) / 9
        for i in range(9):
            self.DepLine.create({
                'asset_id': asset.id,
                'date': fields.Date.today() + relativedelta(months=i),
                'amount': monthly,
            })

        asset._compute_book_value()
        self.assertAlmostEqual(asset.book_value, 1000.0, delta=0.01,
                               msg='Book value should equal salvage value')

    def test_depreciation_line_confirm(self):
        """Depreciation line can be confirmed."""
        asset = self._create_asset(value=12000)
        line = self.DepLine.create({
            'asset_id': asset.id,
            'date': fields.Date.today(),
            'amount': 1000.0,
        })
        self.assertEqual(line.state, 'draft')
        line.action_confirm()
        self.assertEqual(line.state, 'confirmed')

    def test_cascade_delete_depreciation(self):
        """Deleting an asset should cascade-delete depreciation lines."""
        asset = self._create_asset(value=12000)
        line = self.DepLine.create({
            'asset_id': asset.id,
            'date': fields.Date.today(),
            'amount': 1000.0,
        })
        line_id = line.id
        asset.unlink()
        remaining = self.DepLine.search([('id', '=', line_id)])
        self.assertEqual(len(remaining), 0)
