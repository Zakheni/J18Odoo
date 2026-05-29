from odoo import _, api, fields, models


class TaxTableAutofetchSetup(models.TransientModel):
    _name = "zakheni.tax_table_autofetch_setup"
    _description = "Tax Table Autofetch Setup"

    url = fields.Char(string="Tax Table JSON URL", required=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    def action_fetch_now(self):
        self.company_id.write({
            "tax_table_autofetch_url": self.url,
            "tax_table_autofetch_enabled": True,
        })
        self.company_id.action_autofetch_tax_tables()
        return {"type": "ir.actions.act_window_close"}

    def action_setup_cron(self):
        company = self.company_id
        company.tax_table_autofetch_url = self.url
        company.tax_table_autofetch_enabled = True
        existing = self.env["ir.cron"].search([
            ("model_id.model", "=", "res.company"),
            ("code", "=", "model.action_autofetch_tax_tables()"),
        ], limit=1)
        if not existing:
            self.env["ir.cron"].create({
                "name": "Autofetch SARS Tax Tables",
                "model_id": self.env["ir.model"]._get("res.company").id,
                "code": "model.action_autofetch_tax_tables()",
                "interval_number": 1,
                "interval_type": "months",
                "nextcall": fields.Date.today(),
                "active": True,
            })
        return {"type": "ir.actions.act_window_close"}
