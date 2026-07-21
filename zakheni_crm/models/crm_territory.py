from odoo import api, fields, models


class Territory(models.Model):
    _name = "crm.territory"
    _description = "CRM Territory"
    _rec_name = "name"
    _order = "name"

    name = fields.Char("Territory Name", required=True)
    active = fields.Boolean("Active", default=True)
    code = fields.Char("Code")
    parent_id = fields.Many2one("crm.territory", string="Parent Territory")
    child_ids = fields.One2many("crm.territory", "parent_id", string="Sub-Territories")
    user_ids = fields.Many2many("res.users", string="Assigned Users")
    team_id = fields.Many2one("crm.team", string="Sales Team")
    country_ids = fields.Many2many("res.country", string="Countries")
    state_ids = fields.Many2many("res.country.state", string="States")
    lead_ids = fields.One2many("crm.lead", "territory_id", string="Leads/Opportunities")
    lead_count = fields.Integer("Lead Count", compute="_compute_lead_count")

    def _compute_lead_count(self):
        lead_data = self.env["crm.lead"]._read_group(
            [("territory_id", "in", self.ids), ("active", "=", True)],
            ["territory_id"],
            ["__count"],
        )
        counts = {item["territory_id"][0]: item["__count"] for item in lead_data if item["territory_id"]}
        for terr in self:
            terr.lead_count = counts.get(terr.id, 0)

    @api.model
    def _assign_lead_to_territory(self, lead):
        for territory in self.search([("active", "=", True)]):
            matches = True
            if territory.country_ids and (not lead.country_id or lead.country_id not in territory.country_ids):
                matches = False
            if matches and territory.state_ids and (not lead.state_id or lead.state_id not in territory.state_ids):
                matches = False
            if matches:
                lead.territory_id = territory
                return territory
        return False
