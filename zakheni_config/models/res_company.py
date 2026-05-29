import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    tax_table_autofetch_url = fields.Char(
        string="SARS Tax Table Autofetch URL",
        default="https://raw.githubusercontent.com/Souljah213/sars-tax-tables/master/tax_tables.json",
        help="URL to automatically fetch SARS tax tables from.",
    )
    tax_table_autofetch_enabled = fields.Boolean(
        string="Enable Tax Table Autofetch", default=True
    )

    def _setup_company_defaults(self):
        companies = self.search([])
        for company in companies:
            if not company.currency_id or company.currency_id.name != "ZAR":
                zar = self.env.ref("base.ZAR", raise_if_not_found=False)
                if zar:
                    company.currency_id = zar.id

    def action_autofetch_tax_tables(self):
        for company in self.filtered("tax_table_autofetch_enabled"):
            url = company.tax_table_autofetch_url
            if not url:
                continue
            import requests
            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                _logger.warning(
                    "Failed to fetch SARS tax tables for %s from %s: %s",
                    company.name, url, str(e),
                )
                continue
            wizard = self.env["l10n_za.tax.table.import.wizard"].create({
                "source": "json_text",
                "json_text": resp.text,
                "effective_date": data.get("effective_date") or fields.Date.today(),
                "company_id": company.id,
            })
            try:
                wizard.action_import()
                _logger.info(
                    "SARS tax tables autofetched for %s from %s", company.name, url,
                )
            except Exception as e:
                _logger.warning(
                    "Failed to import SARS tax tables for %s: %s", company.name, str(e),
                )
        return True
