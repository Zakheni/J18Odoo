from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.ticket.team"

    customer_id = fields.Many2one(
        comodel_name="helpdesk.customer",
        string="Managed Customer",
        help="If set, this team is dedicated to supporting a specific customer",
    )
    is_dedicated_team = fields.Boolean(
        string="Dedicated Customer Team",
        compute="_compute_is_dedicated_team",
        store=True,
    )

    def _compute_is_dedicated_team(self):
        for team in self:
            team.is_dedicated_team = bool(team.customer_id)
