from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestAssetMaintenance(TransactionCase):
    """Functional tests for asset maintenance management."""

    def setUp(self):
        super().setUp()
        self.Asset = self.env['asset.asset']
        self.Maintenance = self.env['asset.maintenance']
        self.Category = self.env['asset.category']

        self.category = self.Category.create({
            'name': 'Maint Cat',
            'depreciation_duration_months': 12,
        })
        self.asset = self.Asset.create({
            'name': 'Maintainable Asset',
            'category_id': self.category.id,
            'purchase_value': 50000.0,
        })

    def test_create_maintenance_record(self):
        """Create a preventive maintenance record."""
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'Annual Service',
            'maintenance_type': 'preventive',
            'planned_date': fields.Date.today() + timedelta(days=30),
        })
        self.assertTrue(maint.id)
        self.assertEqual(maint.state, 'draft')
        self.assertEqual(maint.maintenance_type, 'preventive')

    def test_maintenance_state_flow(self):
        """Maintenance state should transition: draft -> planned -> in_progress -> completed."""
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'State Flow Test',
            'planned_date': fields.Date.today(),
        })
        self.assertEqual(maint.state, 'draft')

        maint.action_plan()
        self.assertEqual(maint.state, 'planned')

        maint.action_start()
        self.assertEqual(maint.state, 'in_progress')

        maint.action_complete()
        self.assertEqual(maint.state, 'completed')
        self.assertEqual(maint.completed_date, fields.Date.today())

    def test_maintenance_cancel(self):
        """A planned maintenance can be cancelled."""
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'Cancel Test',
        })
        maint.action_plan()
        maint.action_cancel()
        self.assertEqual(maint.state, 'cancelled')

    def test_corrective_maintenance(self):
        """Create a corrective (reactive) maintenance record."""
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'Emergency Repair',
            'maintenance_type': 'corrective',
            'priority': '3',
        })
        self.assertEqual(maint.maintenance_type, 'corrective')
        self.assertEqual(maint.priority, '3')

    def test_maintenance_cost_recorded(self):
        """Maintenance cost should be stored and trackable."""
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'Cost Test',
            'cost': 2500.0,
        })
        self.assertAlmostEqual(maint.cost, 2500.0, delta=0.01)

    def test_maintenance_assigned_user(self):
        """Maintenance can be assigned to a user."""
        user = self.env.ref('base.user_admin')
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'Assignment Test',
            'assigned_to_id': user.id,
        })
        self.assertEqual(maint.assigned_to_id.id, user.id)

    def test_cascade_delete_maintenance(self):
        """Deleting an asset should cascade-delete its maintenance records."""
        maint = self.Maintenance.create({
            'asset_id': self.asset.id,
            'name': 'Cascade Test',
        })
        maint_id = maint.id
        self.asset.unlink()
        remaining = self.Maintenance.search([('id', '=', maint_id)])
        self.assertEqual(len(remaining), 0,
                         'Maintenance should cascade-delete with asset')
