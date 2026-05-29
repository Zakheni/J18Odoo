import werkzeug

import odoo.http as http
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.myaccount import CustomerPortalHelpdesk


class CustomerPortalHelpdeskCustomer(CustomerPortalHelpdesk):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "ticket_count" in counters:
            partner = request.env.user.partner_id
            customer = request.env["helpdesk.customer"].sudo().search(
                [
                    "|",
                    ("partner_id", "=", partner.commercial_partner_id.id),
                    ("partner_id", "child_of", partner.commercial_partner_id.id),
                ],
                limit=1,
            )
            if customer:
                ticket_count = request.env["helpdesk.ticket"].search_count(
                    [("customer_id", "=", customer.id)]
                )
                values["ticket_count"] = ticket_count
        return values

    def _get_customers(self):
        partner = request.env.user.partner_id
        return (
            request.env["helpdesk.customer"]
            .sudo()
            .search(
                [
                    "|",
                    ("partner_id", "=", partner.commercial_partner_id.id),
                    ("partner_id", "child_of", partner.commercial_partner_id.id),
                ]
            )
        )

    def _get_create_new_ticket_values(self, **kw):
        values = super()._get_create_new_ticket_values(**kw)
        values["customers"] = self._get_customers()
        return values

    def _prepare_submit_ticket_vals(self, **kw):
        vals = super()._prepare_submit_ticket_vals(**kw)
        if kw.get("customer"):
            customer = (
                request.env["helpdesk.customer"]
                .sudo()
                .browse(int(kw["customer"]))
            )
            if customer:
                vals["customer_id"] = customer.id
                if customer.team_id and not vals.get("team_id"):
                    vals["team_id"] = customer.team_id.id
                    vals["stage_id"] = customer.team_id._get_applicable_stages()[:1].id
        return vals
