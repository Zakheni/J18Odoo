from odoo.tests.common import TransactionCase
from odoo import fields


class TestAssetAssignment(TransactionCase):
    """Functional tests for asset assignment and check-in/check-out."""

    def setUp(self):
        super().setUp()
        self.Asset = self.env['asset.asset']
        self.Assignment = self.env['asset.assignment']
        self.Category = self.env['asset.category']
        self.Employee = self.env['hr.employee']

        self.category = self.Category.create({
            'name': 'Test Cat',
            'code': 'TC',
            'depreciation_duration_months': 12,
        })
        self.asset = self.Asset.create({
            'name': 'Assignable Asset',
            'category_id': self.category.id,
            'purchase_value': 10000.0,
        })
        self.employee = self.Employee.create({
            'name': 'John Test',
        })

    def test_assign_asset_to_employee(self):
        """Assigning an asset to an employee should create an assignment record."""
        assignment = self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': self.employee.id,
            'assigned_date': fields.Date.today(),
        })
        self.assertTrue(assignment.id)
        self.assertEqual(assignment.state, 'assigned')
        self.assertEqual(assignment.employee_id.id, self.employee.id)

    def test_current_assignment_computed(self):
        """Asset's assigned_employee_id should reflect the current active assignment."""
        self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': self.employee.id,
            'assigned_date': fields.Date.today(),
        })

        self.asset._compute_current_assignment()
        self.assertEqual(self.asset.assigned_employee_id.id, self.employee.id)
        self.assertEqual(self.asset.assigned_date, fields.Date.today())

    def test_return_asset_clears_current_assignment(self):
        """Returning an asset should clear the current assignment on the asset."""
        assignment = self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': self.employee.id,
            'assigned_date': fields.Date.today(),
        })
        self.asset._compute_current_assignment()
        self.assertTrue(self.asset.assigned_employee_id)

        assignment.action_return()
        self.assertEqual(assignment.state, 'returned')
        self.assertEqual(assignment.returned_date, fields.Date.today())

        self.asset._compute_current_assignment()
        self.assertFalse(self.asset.assigned_employee_id,
                         'Returned asset should have no current assignment')

    def test_multiple_assignments_history(self):
        """Asset should keep full assignment history."""
        emp2 = self.Employee.create({'name': 'Jane Test'})

        a1 = self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': self.employee.id,
            'assigned_date': fields.Date.today(),
        })
        a1.action_return()

        a2 = self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': emp2.id,
            'assigned_date': fields.Date.today(),
        })

        self.asset._compute_current_assignment()
        self.assertEqual(self.asset.assigned_employee_id.id, emp2.id,
                         'Should show latest active assignment')

        all_assignments = self.asset.assignment_ids
        self.assertEqual(len(all_assignments), 2,
                         'Full assignment history should be preserved')

    def test_assignment_department_related(self):
        """Department should be auto-populated from employee."""
        dept = self.env['hr.department'].create({'name': 'Engineering'})
        self.employee.department_id = dept
        assignment = self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': self.employee.id,
            'assigned_date': fields.Date.today(),
        })
        self.assertEqual(assignment.department_id.id, dept.id,
                         'Department should come from employee')

    def test_cascade_delete_assignments(self):
        """Deleting an asset should cascade-delete its assignments."""
        self.Assignment.create({
            'asset_id': self.asset.id,
            'employee_id': self.employee.id,
            'assigned_date': fields.Date.today(),
        })
        assignment_id = self.asset.assignment_ids.id
        self.asset.unlink()
        remaining = self.Assignment.search([('id', '=', assignment_id)])
        self.assertEqual(len(remaining), 0)
