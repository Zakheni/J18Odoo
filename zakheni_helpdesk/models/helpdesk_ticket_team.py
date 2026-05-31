from odoo import api, fields, models


class HelpdeskTicketTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    partner_ids = fields.One2many(
        "res.partner", "helpdesk_team_id", string="Assigned Customers"
    )
