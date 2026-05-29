from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_helpdesk_customer = fields.Boolean(
        string="Is Helpdesk Customer",
        help="Enable this customer to have dedicated helpdesk support",
    )
    helpdesk_customer_id = fields.One2many(
        comodel_name="helpdesk.customer",
        inverse_name="partner_id",
        string="Helpdesk Customer Config",
    )

    def action_setup_helpdesk_customer(self):
        self.ensure_one()
        existing = self.env["helpdesk.customer"].search(
            [("partner_id", "=", self.id)], limit=1
        )
        if existing:
            return {
                "type": "ir.actions.act_window",
                "res_model": "helpdesk.customer",
                "view_mode": "form",
                "res_id": existing.id,
            }
        new_customer = self.env["helpdesk.customer"].create(
            {"name": self.name, "partner_id": self.id}
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "helpdesk.customer",
            "view_mode": "form",
            "res_id": new_customer.id,
        }
