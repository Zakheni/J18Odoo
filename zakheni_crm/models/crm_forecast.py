from odoo import api, fields, models


class Forecast(models.Model):
    _name = "crm.forecast"
    _description = "CRM Forecast"
    _rec_name = "name"
    _order = "date_start desc"

    name = fields.Char("Forecast Name", required=True)
    date_start = fields.Date("Start Date", required=True, default=fields.Date.today)
    date_end = fields.Date("End Date", required=True)
    team_id = fields.Many2one("crm.team", string="Sales Team")
    user_id = fields.Many2one("res.users", string="Salesperson")
    territory_id = fields.Many2one("crm.territory", string="Territory")
    optimistic_amount = fields.Monetary("Optimistic Forecast", compute="_compute_amounts", store=True)
    pessimistic_amount = fields.Monetary("Pessimistic Forecast", compute="_compute_amounts", store=True)
    most_likely_amount = fields.Monetary("Most Likely Forecast", compute="_compute_amounts", store=True)
    weighted_amount = fields.Monetary("Weighted Forecast", compute="_compute_amounts", store=True)
    won_amount = fields.Monetary("Closed Won", compute="_compute_amounts", store=True)
    pipeline_count = fields.Integer("Pipeline Count", compute="_compute_amounts", store=True)
    company_id = fields.Many2one("res.company", string="Company", default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    @api.depends("date_start", "date_end", "team_id", "user_id", "territory_id")
    def _compute_amounts(self):
        for rec in self:
            domain = [
                ("active", "=", True),
                ("date_deadline", ">=", rec.date_start),
                ("date_deadline", "<=", rec.date_end),
            ]
            if rec.team_id:
                domain.append(("team_id", "=", rec.team_id.id))
            if rec.user_id:
                domain.append(("user_id", "=", rec.user_id.id))
            if rec.territory_id:
                domain.append(("territory_id", "=", rec.territory_id.id))

            leads = self.env["crm.lead"].search(domain)
            rec.pipeline_count = len(leads)
            rec.optimistic_amount = sum(
                l.expected_revenue or 0.0 for l in leads
            )
            rec.pessimistic_amount = sum(
                (l.expected_revenue or 0.0) * ((l.probability or 0.0) / 100.0 * 0.5)
                for l in leads
            )
            rec.most_likely_amount = sum(
                (l.expected_revenue or 0.0) * ((l.probability or 0.0) / 100.0)
                for l in leads
            )
            rec.weighted_amount = sum(
                l.forecast_amount or 0.0 for l in leads
            )
            rec.won_amount = sum(
                (l.expected_revenue or 0.0) for l in leads
                if l.stage_id.is_won
            )
