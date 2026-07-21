from odoo import api, fields, models


class LeadGrade(models.Model):
    _name = "crm.lead.grade"
    _description = "Lead Grade"
    _rec_name = "name"
    _order = "sequence, min_score desc"

    name = fields.Char("Grade Name", required=True)
    code = fields.Char("Grade Code", required=True)
    sequence = fields.Integer("Sequence", default=10)
    active = fields.Boolean("Active", default=True)
    min_score = fields.Integer("Minimum Score", required=True, default=0)
    color = fields.Integer("Color Index", default=0)
    description = fields.Text("Description")
    lead_ids = fields.One2many("crm.lead", "lead_grade_id", string="Leads")
    lead_count = fields.Integer("Lead Count", compute="_compute_lead_count")

    def _compute_lead_count(self):
        lead_data = self.env["crm.lead"]._read_group(
            [("lead_grade_id", "in", self.ids), ("active", "=", True)],
            ["lead_grade_id"],
            ["__count"],
        )
        counts = {item["lead_grade_id"][0]: item["__count"] for item in lead_data if item["lead_grade_id"]}
        for grade in self:
            grade.lead_count = counts.get(grade.id, 0)
