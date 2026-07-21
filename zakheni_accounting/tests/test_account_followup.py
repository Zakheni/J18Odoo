from odoo.tests.common import TransactionCase
from odoo import fields
from datetime import timedelta


class TestFollowUpFunctional(TransactionCase):
    """Functional tests for follow-up plans, levels, escalation, and cron."""

    def setUp(self):
        super().setUp()
        self.Plan = self.env['zakheni.followup.plan']
        self.Level = self.env['zakheni.followup.level']
        self.Move = self.env['account.move']
        self.Partner = self.env['res.partner']

    def _create_invoice(self, partner, amount=1000, due_days_ago=0):
        due = fields.Date.today() - timedelta(days=due_days_ago)
        inv = self.Move.create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'invoice_date': due,
            'invoice_date_due': due,
            'invoice_line_ids': [(0, 0, {
                'name': 'Follow-up test',
                'quantity': 1,
                'price_unit': amount,
            })],
        })
        inv.action_post()
        return inv

    def _create_standard_plan(self):
        plan = self.Plan.create({'name': 'Standard Plan', 'sequence': 1})
        self.Level.create({
            'plan_id': plan.id, 'name': 'Level 1 - Friendly',
            'days_offset': 0, 'sequence': 10, 'send_email': True,
        })
        self.Level.create({
            'plan_id': plan.id, 'name': 'Level 2 - Second Notice',
            'days_offset': 7, 'sequence': 20, 'send_email': True,
        })
        self.Level.create({
            'plan_id': plan.id, 'name': 'Level 3 - Final',
            'days_offset': 14, 'sequence': 30, 'send_letter': True,
        })
        self.Level.create({
            'plan_id': plan.id, 'name': 'Level 4 - Collections',
            'days_offset': 30, 'sequence': 40, 'manual_action': True,
        })
        return plan

    def test_followup_plan_created_with_levels(self):
        """A plan with multiple levels should cascade save correctly."""
        plan = self._create_standard_plan()
        self.assertEqual(len(plan.level_ids), 4)
        names = plan.level_ids.mapped('name')
        self.assertIn('Level 1 - Friendly', names)
        self.assertIn('Level 4 - Collections', names)

    def test_followup_level_order_by_days_offset(self):
        """Levels should be ordered by days_offset within a plan."""
        plan = self.Plan.create({'name': 'Ordered Plan'})
        self.Level.create({
            'plan_id': plan.id, 'name': 'Late', 'days_offset': 30, 'sequence': 10,
        })
        self.Level.create({
            'plan_id': plan.id, 'name': 'Early', 'days_offset': 0, 'sequence': 20,
        })
        self.assertEqual(plan.level_ids[0].name, 'Early')

    def test_assign_followup_plan_to_partner(self):
        """A partner should be assignable to a follow-up plan."""
        plan = self._create_standard_plan()
        partner = self.Partner.create({
            'name': 'Test Customer',
            'customer_rank': 1,
            'followup_plan_id': plan.id,
        })
        self.assertEqual(partner.followup_plan_id.id, plan.id)

    def test_followup_plan_id_related_on_invoice(self):
        """Invoice's followup_plan_id should be related to the partner's plan."""
        plan = self._create_standard_plan()
        partner = self.Partner.create({
            'name': 'Rel Test', 'customer_rank': 1, 'followup_plan_id': plan.id,
        })
        inv = self._create_invoice(partner=partner, amount=10000, due_days_ago=5)
        self.assertEqual(inv.followup_plan_id.id, plan.id,
                         'Invoice should inherit partner follow-up plan')

    def test_action_send_followup_escalates_level(self):
        """action_send_followup() should advance to the next level."""
        plan = self._create_standard_plan()
        partner = self.Partner.create({
            'name': 'Escalate', 'customer_rank': 1, 'followup_plan_id': plan.id,
        })
        inv = self._create_invoice(partner=partner, amount=10000, due_days_ago=10)
        self.assertFalse(inv.followup_level_id,
                         'No follow-up level initially')

        inv.action_send_followup()
        self.assertTrue(inv.followup_level_id,
                        'Follow-up level should be assigned')
        self.assertEqual(inv.followup_level_id.name, 'Level 1 - Friendly',
                         'Should start at level 1')
        self.assertEqual(inv.followup_date, fields.Date.today())

        inv.action_send_followup()
        self.assertEqual(inv.followup_level_id.name, 'Level 2 - Second Notice',
                         'Should escalate to level 2')

    def test_cron_auto_followup_processes_overdue_invoices(self):
        """_cron_auto_followup() should escalate all overdue invoices with plans."""
        plan = self._create_standard_plan()
        p1 = self.Partner.create({
            'name': 'Cron A', 'customer_rank': 1, 'followup_plan_id': plan.id,
        })
        p2 = self.Partner.create({
            'name': 'Cron B', 'customer_rank': 1, 'followup_plan_id': plan.id,
        })
        inv1 = self._create_invoice(partner=p1, amount=5000, due_days_ago=5)
        inv2 = self._create_invoice(partner=p2, amount=8000, due_days_ago=10)

        self.env['account.move']._cron_auto_followup()

        self.assertTrue(inv1.followup_level_id,
                        'inv1 should have follow-up after cron')
        self.assertTrue(inv2.followup_level_id,
                        'inv2 should have follow-up after cron')

    def test_cron_skips_invoices_without_plan(self):
        """_cron_auto_followup() should skip invoices without a follow-up plan."""
        partner = self.Partner.create({'name': 'No Plan', 'customer_rank': 1})
        inv = self._create_invoice(partner=partner, amount=5000, due_days_ago=30)
        self.env['account.move']._cron_auto_followup()
        self.assertFalse(inv.followup_level_id,
                         'Invoice without plan should not get follow-up')

    def test_in_followup_computed_field(self):
        """in_followup should be True when follow-up level is set."""
        plan = self._create_standard_plan()
        partner = self.Partner.create({
            'name': 'InFup', 'customer_rank': 1, 'followup_plan_id': plan.id,
        })
        inv = self._create_invoice(partner=partner, amount=5000, due_days_ago=5)
        self.assertFalse(inv.in_followup)
        inv.action_send_followup()
        self.assertTrue(inv.in_followup)

    def test_dunning_levels_have_required_fields(self):
        """Each follow-up level should have required configuration fields."""
        level = self.Level.create({
            'plan_id': self._create_standard_plan().id,
            'name': 'Custom Level',
            'days_offset': 5,
            'sequence': 50,
        })
        self.assertTrue(level.send_email, 'Email should default to True')
        self.assertFalse(level.send_letter, 'Letter should default to False')
        self.assertFalse(level.manual_action, 'Manual action defaults to False')
        self.assertTrue(level.active, 'Level should be active by default')

    def test_plan_ordering(self):
        """Plans should be ordered by sequence."""
        p1 = self.Plan.create({'name': 'B Plan', 'sequence': 20})
        p2 = self.Plan.create({'name': 'A Plan', 'sequence': 10})
        plans = self.Plan.search([('id', 'in', [p1.id, p2.id])], order='sequence')
        self.assertEqual(plans[0].name, 'A Plan')

    def test_dunning_level_cascade_delete(self):
        """Deleting a plan should cascade-delete its levels."""
        plan = self._create_standard_plan()
        level_ids = plan.level_ids.ids
        self.assertTrue(level_ids)
        plan.unlink()
        remaining = self.Level.search([('id', 'in', level_ids)])
        self.assertEqual(len(remaining), 0,
                         'Levels should be cascade-deleted with plan')
