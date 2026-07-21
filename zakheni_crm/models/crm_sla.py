from datetime import timedelta

from odoo import api, fields, models


class Sla(models.Model):
    _name = "crm.sla"
    _description = "CRM SLA Policy"
    _rec_name = "name"
    _order = "name"

    name = fields.Char("SLA Name", required=True)
    active = fields.Boolean("Active", default=True)
    hours = fields.Float("Response Hours", required=True, default=24.0,
        help="Maximum hours to respond within")
    stage_id = fields.Many2one("crm.stage", string="Target Stage",
        help="SLA counts time spent in this stage")
    team_id = fields.Many2one("crm.team", string="Sales Team")
    priority = fields.Selection([
        ("0", "Low"),
        ("1", "Medium"),
        ("2", "High"),
        ("3", "Very High"),
    ], string="Minimum Priority", default="0")
    success_count = fields.Integer("Met SLA Count", default=0)
    breach_count = fields.Integer("Breached SLA Count", default=0)
    sla_percentage = fields.Float("SLA Achievement %", compute="_compute_sla_percentage")

    def _compute_sla_percentage(self):
        for sla in self:
            total = sla.success_count + sla.breach_count
            sla.sla_percentage = round((sla.success_count / total * 100.0), 1) if total else 0.0

    def _compute_deadline(self, start_date):
        self.ensure_one()
        if not start_date:
            return False
        return start_date + timedelta(hours=self.hours)

    def _add_sla_success(self):
        self.ensure_one()
        self.success_count += 1

    def _add_sla_breach(self):
        self.ensure_one()
        self.breach_count += 1
