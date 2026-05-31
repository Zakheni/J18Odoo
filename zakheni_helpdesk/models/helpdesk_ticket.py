from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    def _auto_route_to_partner_team(self):
        for ticket in self:
            partner = ticket.partner_id
            if not partner:
                partner = ticket.commercial_partner_id
            if partner and partner.helpdesk_team_id and not ticket.team_id:
                ticket.team_id = partner.helpdesk_team_id

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        tickets._auto_route_to_partner_team()
        return tickets

    def write(self, vals):
        res = super().write(vals)
        if vals.get("partner_id"):
            self._auto_route_to_partner_team()
        return res
