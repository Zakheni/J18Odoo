from odoo import api, fields, models


class Competitor(models.Model):
    _name = "crm.competitor"
    _description = "Competitor"
    _rec_name = "name"
    _order = "name"

    name = fields.Char("Competitor Name", required=True)
    active = fields.Boolean("Active", default=True)
    website = fields.Char("Website")
    partner_id = fields.Many2one("res.partner", string="Related Partner")
    product_description = fields.Text("Key Products/Services")
    strength_ids = fields.Many2many("crm.competitor.attribute", relation="crm_competitor_strength_rel", string="Strengths")
    weakness_ids = fields.Many2many("crm.competitor.attribute", relation="crm_competitor_weakness_rel", string="Weaknesses")
    lead_count = fields.Integer("Deal Count", compute="_compute_lead_count")
    lead_ids = fields.One2many("crm.lead", "competitor_id", string="Related Deals")

    def _compute_lead_count(self):
        lead_data = self.env["crm.lead"]._read_group(
            [("competitor_id", "in", self.ids), ("active", "=", True)],
            ["competitor_id"],
            ["__count"],
        )
        counts = {item["competitor_id"][0]: item["__count"] for item in lead_data if item["competitor_id"]}
        for comp in self:
            comp.lead_count = counts.get(comp.id, 0)


class CompetitorAttribute(models.Model):
    _name = "crm.competitor.attribute"
    _description = "Competitor Attribute"
    _rec_name = "name"

    name = fields.Char("Attribute", required=True)
    category = fields.Selection([
        ("strength", "Strength"),
        ("weakness", "Weakness"),
    ], string="Category")
