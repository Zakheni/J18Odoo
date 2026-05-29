from odoo import api, fields, models


class HelpdeskCustomer(models.Model):
    _name = "helpdesk.customer"
    _description = "Helpdesk Customer"
    _inherit = ["mail.alias.mixin"]
    _order = "sequence, name"
    _rec_name = "name"

    sequence = fields.Integer(default=10)
    name = fields.Char(string="Customer Name", required=True)
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        domain=[("is_company", "=", True)],
        help="The company partner record for this customer",
    )
    active = fields.Boolean(default=True)
    team_id = fields.Many2one(
        comodel_name="helpdesk.ticket.team",
        string="Assigned Team",
        domain=[("customer_id", "=", False)],
        help="The helpdesk team that handles this customer's tickets",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    ticket_count = fields.Integer(
        string="Ticket Count", compute="_compute_ticket_count"
    )
    open_ticket_count = fields.Integer(
        string="Open Tickets", compute="_compute_ticket_count"
    )
    color = fields.Integer(string="Color Index", default=0)

    def _compute_ticket_count(self):
        for record in self:
            tickets = self.env["helpdesk.ticket"].search(
                [("customer_id", "=", record.id)]
            )
            record.ticket_count = len(tickets)
            record.open_ticket_count = len(
                tickets.filtered(lambda t: not t.stage_id.closed)
            )

    def _alias_get_creation_values(self):
        values = super()._alias_get_creation_values()
        values["alias_model_id"] = self.env.ref(
            "helpdesk_mgmt.model_helpdesk_ticket"
        ).id
        values["alias_parent_model_id"] = self.env.ref(
            "helpdesk_mgmt.model_helpdesk_ticket_team"
        ).id
        values["alias_defaults"] = defaults = (
            f'{{"customer_id": {self.id}}}'
        )
        return values

    def _get_customer_tickets_domain(self):
        return [("customer_id", "=", self.id)]

    def action_open_tickets(self):
        self.ensure_one()
        return {
            "name": f"Tickets - {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.ticket",
            "view_mode": "kanban,list,form",
            "domain": self._get_customer_tickets_domain(),
            "context": {"default_customer_id": self.id},
        }
