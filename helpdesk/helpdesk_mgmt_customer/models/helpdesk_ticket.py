from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    customer_id = fields.Many2one(
        comodel_name="helpdesk.customer",
        string="Customer Account",
        index=True,
        tracking=True,
        help="The helpdesk customer this ticket belongs to",
    )

    def _get_customer_email_alias_domain(self):
        self.ensure_one()
        if self.customer_id and self.customer_id.alias_id:
            return self.customer_id.alias_id.alias_name
        return super()._get_customer_email_alias_domain()

    @api.model
    def message_new(self, msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        if "customer_id" not in custom_values:
            to_email = (msg.get("to") or "") + "," + (msg.get("cc") or "")
            customer = self._find_customer_from_email(to_email)
            if customer:
                custom_values["customer_id"] = customer.id
                if not custom_values.get("team_id") and customer.team_id:
                    custom_values["team_id"] = customer.team_id.id
        return super().message_new(msg, custom_values=custom_values)

    @api.model
    def _find_customer_from_email(self, email_string):
        alias_model = self.env["mail.alias"]
        email_parts = [
            e.strip().lower() for e in email_string.split(",") if e.strip()
        ]
        for email in email_parts:
            local_part = email.split("@")[0] if "@" in email else email
            alias = alias_model.search(
                [("alias_name", "=", local_part)], limit=1
            )
            if alias:
                customer = self.env["helpdesk.customer"].search(
                    [("alias_id", "=", alias.id)], limit=1
                )
                if customer:
                    return customer
        return self.env["helpdesk.customer"]

    @api.model
    def _find_customer_from_partner(self, partner):
        if not partner:
            return self.env["helpdesk.customer"]
        return self.env["helpdesk.customer"].search(
            [
                "|",
                ("partner_id", "=", partner.commercial_partner_id.id),
                ("partner_id", "child_of", partner.commercial_partner_id.id),
            ],
            limit=1,
        )

    def _notify_get_reply_to(self, default=None):
        aliases = {}
        for ticket in self:
            if ticket.customer_id and ticket.customer_id.alias_id:
                aliases[ticket.id] = ticket.customer_id.alias_id.alias_name
            elif ticket.team_id:
                aliases[ticket.id] = (
                    ticket.team_id._notify_get_reply_to(default=default).get(
                        ticket.team_id.id
                    )
                )
        return aliases
