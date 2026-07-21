from odoo import api, fields, models


class LeadScore(models.Model):
    _name = "crm.lead.score"
    _description = "Lead Score Entry"
    _rec_name = "lead_id"
    _order = "write_date desc"

    lead_id = fields.Many2one("crm.lead", string="Lead", required=True, ondelete="cascade")
    rule_id = fields.Many2one("crm.scoring.rule", string="Scoring Rule", required=True, ondelete="cascade")
    score = fields.Integer("Score", required=True, default=0)
    rule_category = fields.Selection(related="rule_id.category", store=True)
    rule_name = fields.Char(related="rule_id.name", store=True)
