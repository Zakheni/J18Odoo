from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    helpdesk_team_id = fields.Many2one(
        "helpdesk.ticket.team",
        string="Helpdesk Team",
        help="When set, tickets created for this customer are automatically routed to this team.",
    )
