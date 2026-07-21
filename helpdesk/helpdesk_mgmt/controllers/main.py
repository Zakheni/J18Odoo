import base64
import logging

import werkzeug
import werkzeug.urls

import odoo.http as http
from odoo.http import request
from odoo.tools import plaintext2html

_logger = logging.getLogger(__name__)


class HelpdeskTicketController(http.Controller):
    @http.route("/ticket/close", type="http", auth="public")
    def support_ticket_close(self, **kw):
        """Close the support ticket"""
        values = {}
        for field_name, field_value in kw.items():
            if field_name.endswith("_id"):
                values[field_name] = int(field_value)
            else:
                values[field_name] = field_value
        ticket = (
            http.request.env["helpdesk.ticket"]
            .sudo()
            .search([("id", "=", values["ticket_id"])])
        )
        stage = http.request.env["helpdesk.ticket.stage"].browse(values.get("stage_id"))
        if stage.close_from_portal:
            ticket.stage_id = values.get("stage_id")

        return werkzeug.utils.redirect("/my/ticket/" + str(ticket.id))

    def _get_teams(self):
        return (
            http.request.env["helpdesk.ticket.team"]
            .with_company(request.env.company.id)
            .search([("active", "=", True), ("show_in_portal", "=", True)])
            if http.request.env.user.company_id.helpdesk_mgmt_portal_select_team
            else False
        )

    def _get_categories(self, **kw):
        company = request.env.company
        category_model = http.request.env["helpdesk.ticket.category"]
        return category_model.with_company(company.id).search([("active", "=", True)])

    def _get_or_create_partner(self, email, name):
        if not email:
            return request.env.user.partner_id
        partner = request.env["res.partner"].sudo().search([("email", "=ilike", email)], limit=1)
        if partner:
            return partner
        return request.env["res.partner"].sudo().create({
            "name": name or email,
            "email": email,
        })

    @http.route("/new/ticket", type="http", auth="public", website=True)
    def create_new_ticket(self, **kw):
        values = self._get_create_new_ticket_values(**kw)
        if kw.get("success"):
            values["success"] = True
            values["ticket_ref"] = kw.get("ticket_ref", "")
        return http.request.render("helpdesk_mgmt.portal_create_ticket", values)

    def _get_create_new_ticket_values(self, **kw):
        session_info = http.request.env["ir.http"].session_info()
        company = request.env.company
        user = request.env.user
        is_public = user._is_public()
        email = kw.get("partner_email", "") if is_public else user.email or ""
        name = kw.get("partner_name", "") if is_public else user.name or ""
        company = request.env.company
        return {
            "categories": self._get_categories(**kw),
            "teams": self._get_teams(),
            "email": email,
            "name": name,
            "is_public": is_public,
            "ticket_team_id_required": (company.helpdesk_mgmt_portal_team_id_required),
            "ticket_category_id_required": (
                company.helpdesk_mgmt_portal_category_id_required
            ),
            "max_upload_size": session_info["max_file_upload_size"],
        }

    def _prepare_submit_ticket_vals(self, **kw):
        category = http.request.env["helpdesk.ticket.category"].browse(
            int(kw.get("category") or 0)
        )
        company = category.company_id or http.request.env.company
        partner = self._get_or_create_partner(
            kw.get("partner_email", ""), kw.get("partner_name", "")
        )
        vals = {
            "company_id": company.id,
            "category_id": category.id,
            "description": plaintext2html(kw.get("description")),
            "name": kw.get("subject"),
            "attachment_ids": False,
            "channel_id": request.env.ref(
                "helpdesk_mgmt.helpdesk_ticket_channel_web", False
            ).id,
            "partner_id": partner.id,
            "partner_name": partner.name,
            "partner_email": partner.email,
            "user_id": False,
        }
        team = http.request.env["helpdesk.ticket.team"]
        if company.helpdesk_mgmt_portal_select_team and kw.get("team"):
            team = (
                http.request.env["helpdesk.ticket.team"]
                .sudo()
                .search(
                    [("id", "=", int(kw.get("team"))), ("show_in_portal", "=", True)]
                )
            )
        if not team:
            team = (
                http.request.env["helpdesk.ticket.team"]
                .sudo()
                .search([("show_in_portal", "=", True)], limit=1)
            )
        if team:
            vals["team_id"] = team.id
        stage = team._get_applicable_stages()[:1]
        if stage:
            vals["stage_id"] = stage.id
        return vals

    @http.route("/submitted/ticket", type="http", auth="public", website=True, csrf=True)
    def submit_ticket(self, **kw):
        vals = self._prepare_submit_ticket_vals(**kw)
        new_ticket = request.env["helpdesk.ticket"].sudo().create(vals)
        partner = request.env["res.partner"].sudo().browse(vals["partner_id"])
        if partner != request.env.user.partner_id:
            new_ticket.message_subscribe(partner_ids=partner.ids)
        if kw.get("attachment"):
            for c_file in request.httprequest.files.getlist("attachment"):
                data = c_file.read()
                if c_file.filename:
                    request.env["ir.attachment"].sudo().create(
                        {
                            "name": c_file.filename,
                            "datas": base64.b64encode(data),
                            "res_model": "helpdesk.ticket",
                            "res_id": new_ticket.id,
                        }
                    )
        query = werkzeug.urls.url_encode({
            "success": 1,
            "ticket_ref": new_ticket.display_name or new_ticket.id,
        })
        return werkzeug.utils.redirect(f"/new/ticket?{query}")
