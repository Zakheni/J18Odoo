import json

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class L10nZaTaxTableImportWizard(models.TransientModel):
    _name = "l10n_za.tax.table.import.wizard"
    _description = "Import SARS Tax Tables"

    source = fields.Selection(
        [("json_text", "Paste JSON"), ("json_url", "Download from URL")],
        string="Import Source",
        default="json_text",
        required=True,
    )
    json_text = fields.Text(string="Tax Tables JSON", help="Paste the tax table JSON data here.")
    json_url = fields.Char(string="JSON URL", help="URL to download tax tables from.")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    effective_date = fields.Date(string="Effective Date", required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [("choose", "Choose"), ("preview", "Preview"), ("done", "Done")],
        default="choose",
    )
    preview_data = fields.Text(string="Preview", readonly=True)

    def action_preview(self):
        self.ensure_one()
        data = self._get_json_data()
        tables = data.get("tables", {})
        preview_lines = []
        version = data.get("version", "N/A")
        eff_date = data.get("effective_date", str(self.effective_date))
        preview_lines.append("Version: %s" % version)
        preview_lines.append("Effective Date: %s" % eff_date)
        preview_lines.append("")

        if tables.get("paye_brackets"):
            preview_lines.append("PAYE Tax Brackets:")
            for b in tables["paye_brackets"]:
                to_str = "R%s" % b["to"] if b.get("to") else "R inf"
                preview_lines.append(
                    "  R%s - %s: %.2f%% (base: R%s)" % (b["from"], to_str, b["rate"], b.get("base", 0))
                )
            preview_lines.append("")

        if tables.get("rebates"):
            preview_lines.append("Tax Rebates (annual):")
            for k, v in tables["rebates"].items():
                preview_lines.append("  %s: R%s" % (k, v))
            preview_lines.append("")

        if tables.get("medical_credits"):
            preview_lines.append("Medical Tax Credits (monthly):")
            for k, v in tables["medical_credits"].items():
                preview_lines.append("  %s: R%s" % (k, v))
            preview_lines.append("")

        if tables.get("uif"):
            preview_lines.append("UIF:")
            preview_lines.append("  Ceiling: R%s" % tables["uif"].get("ceiling", "N/A"))
            preview_lines.append("  Rate: %s%%" % tables["uif"].get("rate", "N/A"))
            preview_lines.append("")

        if tables.get("sdl"):
            preview_lines.append("SDL:")
            preview_lines.append("  Ceiling: R%s" % tables["sdl"].get("ceiling", "N/A"))
            preview_lines.append("  Rate: %s%%" % tables["sdl"].get("rate", "N/A"))

        self.write({
            "state": "preview",
            "preview_data": "\n".join(preview_lines),
        })
        return {
            "type": "ir.actions.act_window",
            "res_model": "l10n_za.tax.table.import.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_import(self):
        self.ensure_one()
        data = self._get_json_data()
        tables = data.get("tables", {})
        company = self.company_id or self.env.company
        effective_date = self.effective_date

        if tables.get("paye_brackets"):
            self._update_paye_brackets(tables["paye_brackets"], effective_date, company)
        if tables.get("rebates"):
            self._update_rebates(tables["rebates"], effective_date, company)
        if tables.get("medical_credits"):
            self._update_medical_credits(tables["medical_credits"], effective_date, company)
        if tables.get("uif"):
            self._update_uif(tables["uif"], effective_date, company)
        if tables.get("sdl"):
            self._update_sdl(tables["sdl"], effective_date, company)

        self.write({"state": "done"})
        return {
            "type": "ir.actions.act_window",
            "res_model": "l10n_za.tax.table.import.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    @api.model
    def _update_paye_brackets(self, brackets_data, effective_date, company):
        param = self.env["hr.rule.parameter"].search([
            ("code", "=", "l10n_za_paye_brackets"),
            ("date_from", "=", effective_date),
            ("company_id", "=", company.id),
        ], limit=1)
        if not param:
            param = self.env["hr.rule.parameter"].create({
                "code": "l10n_za_paye_brackets",
                "name": "PAYE Tax Brackets (%s)" % effective_date.strftime("%Y/%m"),
                "date_from": effective_date,
                "value": 1,
                "company_id": company.id,
            })
        self.env["hr.rule.parameter.bracket"].search([
            ("parameter_id", "=", param.id),
        ]).unlink()
        for i, bracket in enumerate(brackets_data):
            self.env["hr.rule.parameter.bracket"].create({
                "parameter_id": param.id,
                "sequence": (i + 1) * 10,
                "from_amount": bracket.get("from", 0.0),
                "to_amount": bracket.get("to"),
                "rate": bracket.get("rate", 0.0),
                "base_amount": bracket.get("base", 0.0),
            })

    @api.model
    def _update_rebates(self, rebates_data, effective_date, company):
        mapping = {
            "primary": "l10n_za_rebate_primary",
            "secondary": "l10n_za_rebate_secondary",
            "tertiary": "l10n_za_rebate_tertiary",
        }
        names = {
            "l10n_za_rebate_primary": "Primary Tax Rebate (%s)",
            "l10n_za_rebate_secondary": "Secondary Tax Rebate - 65+ (%s)",
            "l10n_za_rebate_tertiary": "Tertiary Tax Rebate - 75+ (%s)",
        }
        for key, code in mapping.items():
            if key in rebates_data:
                label = (names.get(code, "%s") % effective_date.strftime("%Y/%m"))
                self._create_or_update_param(code, effective_date, rebates_data[key], company, label)

    @api.model
    def _update_medical_credits(self, medical_data, effective_date, company):
        main = medical_data.get("main_member")
        if main is not None:
            self._create_or_update_param(
                "l10n_za_medical_credit_main", effective_date, main, company,
                "Medical Tax Credit - Main Member (monthly) (%s)" % effective_date.strftime("%Y/%m"),
            )
        dep = medical_data.get("dependent")
        if dep is not None:
            self._create_or_update_param(
                "l10n_za_medical_credit_dependent", effective_date, dep, company,
                "Medical Tax Credit - Dependent (monthly) (%s)" % effective_date.strftime("%Y/%m"),
            )

    @api.model
    def _update_uif(self, uif_data, effective_date, company):
        ceiling = uif_data.get("ceiling")
        rate = uif_data.get("rate")
        if ceiling is not None:
            self._create_or_update_param(
                "l10n_za_uif_ceiling", effective_date, ceiling, company,
                "UIF Earnings Ceiling (monthly) (%s)" % effective_date.strftime("%Y/%m"),
            )
        if rate is not None:
            self._create_or_update_param(
                "l10n_za_uif_rate", effective_date, rate, company,
                "UIF Contribution Rate (%s)" % effective_date.strftime("%Y/%m"),
            )

    @api.model
    def _update_sdl(self, sdl_data, effective_date, company):
        ceiling = sdl_data.get("ceiling")
        rate = sdl_data.get("rate")
        if ceiling is not None:
            self._create_or_update_param(
                "l10n_za_sdl_ceiling", effective_date, ceiling, company,
                "SDL Maximum Contribution (monthly) (%s)" % effective_date.strftime("%Y/%m"),
            )
        if rate is not None:
            self._create_or_update_param(
                "l10n_za_sdl_rate", effective_date, rate, company,
                "SDL Contribution Rate (%s)" % effective_date.strftime("%Y/%m"),
            )

    @api.model
    def _create_or_update_param(self, code, effective_date, value, company, name):
        existing = self.env["hr.rule.parameter"].search([
            ("code", "=", code),
            ("date_from", "=", effective_date),
            ("company_id", "=", company.id),
        ], limit=1)
        if existing:
            existing.write({"value": value})
        else:
            self.env["hr.rule.parameter"].create({
                "code": code,
                "name": name,
                "date_from": effective_date,
                "value": value,
                "company_id": company.id,
            })

    def _get_json_data(self):
        self.ensure_one()
        if self.source == "json_text":
            if not self.json_text:
                raise UserError(_("Please paste the JSON tax table data."))
            try:
                data = json.loads(self.json_text)
            except json.JSONDecodeError as e:
                raise UserError(_("Invalid JSON: %s") % str(e))
        else:
            if not self.json_url:
                raise UserError(_("Please enter a URL."))
            try:
                import requests
                resp = requests.get(self.json_url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                raise UserError(_("Failed to fetch from URL: %s") % str(e))

        if "tables" not in data:
            raise UserError(_("Invalid tax table format: missing 'tables' key."))
        return data
