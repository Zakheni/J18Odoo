from odoo import api, fields, models


class CrmTarget(models.Model):
    _name = "crm.target"
    _description = "Sales Target"
    _rec_name = "display_name"
    _order = "date_from desc, user_id"

    display_name = fields.Char(compute="_compute_display_name", store=True)
    user_id = fields.Many2one("res.users", string="Salesperson", required=True)
    team_id = fields.Many2one("crm.team", string="Sales Team")
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    revenue_target = fields.Monetary(string="Revenue Target", currency_field="currency_id")
    deals_target = fields.Integer(string="Deals Target")
    leads_target = fields.Integer(string="Leads Target")
    revenue_achieved = fields.Monetary(
        string="Revenue Achieved", compute="_compute_achieved", store=True,
        currency_field="currency_id",
    )
    deals_achieved = fields.Integer(
        string="Deals Achieved", compute="_compute_achieved", store=True,
    )
    leads_generated = fields.Integer(
        string="Leads Generated", compute="_compute_achieved", store=True,
    )
    revenue_progress = fields.Float(
        string="Revenue Progress (%)", compute="_compute_progress", store=True,
    )
    deals_progress = fields.Float(
        string="Deals Progress (%)", compute="_compute_progress", store=True,
    )
    leads_progress = fields.Float(
        string="Leads Progress (%)", compute="_compute_progress", store=True,
    )
    company_id = fields.Many2one("res.company", string="Company",
        default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    @api.depends("user_id", "date_from", "date_to")
    def _compute_display_name(self):
        for rec in self:
            parts = [
                rec.user_id.name or "",
                rec.date_from and rec.date_from.strftime("%Y-%m-%d") or "",
                rec.date_to and rec.date_to.strftime("%Y-%m-%d") or "",
            ]
            rec.display_name = " — ".join(parts)

    @api.depends("date_from", "date_to", "user_id", "team_id")
    def _compute_achieved(self):
        for rec in self:
            domain = [
                ("active", "=", True),
                ("date_deadline", ">=", rec.date_from),
                ("date_deadline", "<=", rec.date_to),
                ("user_id", "=", rec.user_id.id),
            ]
            if rec.team_id:
                domain.append(("team_id", "=", rec.team_id.id))
            leads = self.env["crm.lead"].search(domain)
            won = leads.filtered(lambda l: l.stage_id.is_won)
            rec.revenue_achieved = sum(l.expected_revenue or 0.0 for l in won)
            rec.deals_achieved = len(won)
            rec.leads_generated = len(leads)

    @api.depends("revenue_target", "revenue_achieved", "deals_target", "deals_achieved",
                 "leads_target", "leads_generated")
    def _compute_progress(self):
        for rec in self:
            rec.revenue_progress = (
                (rec.revenue_achieved / rec.revenue_target * 100)
                if rec.revenue_target else 0.0
            )
            rec.deals_progress = (
                (rec.deals_achieved / rec.deals_target * 100)
                if rec.deals_target else 0.0
            )
            rec.leads_progress = (
                (rec.leads_generated / rec.leads_target * 100)
                if rec.leads_target else 0.0
            )


class CrmCompanyTarget(models.Model):
    _name = "crm.company.target"
    _description = "Company Target"
    _rec_name = "display_name"
    _order = "date_from desc"

    display_name = fields.Char(compute="_compute_display_name", store=True)
    name = fields.Char(string="Target Name")
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)
    revenue_target = fields.Monetary(string="Revenue Target", currency_field="currency_id")
    deals_target = fields.Integer(string="Deals Target")
    leads_target = fields.Integer(string="Leads Target")
    revenue_achieved = fields.Monetary(
        string="Revenue Achieved", compute="_compute_achieved", store=True,
        currency_field="currency_id",
    )
    deals_achieved = fields.Integer(
        string="Deals Achieved", compute="_compute_achieved", store=True,
    )
    leads_generated = fields.Integer(
        string="Leads Generated", compute="_compute_achieved", store=True,
    )
    revenue_progress = fields.Float(
        string="Revenue Progress (%)", compute="_compute_progress", store=True,
    )
    deals_progress = fields.Float(
        string="Deals Progress (%)", compute="_compute_progress", store=True,
    )
    leads_progress = fields.Float(
        string="Leads Progress (%)", compute="_compute_progress", store=True,
    )
    company_id = fields.Many2one("res.company", string="Company",
        default=lambda self: self.env.company)
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    @api.depends("name", "date_from", "date_to")
    def _compute_display_name(self):
        for rec in self:
            if rec.name:
                rec.display_name = rec.name
            else:
                parts = [
                    rec.date_from and rec.date_from.strftime("%Y-%m-%d") or "",
                    rec.date_to and rec.date_to.strftime("%Y-%m-%d") or "",
                ]
                rec.display_name = " — ".join(parts)

    @api.depends("date_from", "date_to")
    def _compute_achieved(self):
        for rec in self:
            domain = [
                ("active", "=", True),
                ("date_deadline", ">=", rec.date_from),
                ("date_deadline", "<=", rec.date_to),
            ]
            leads = self.env["crm.lead"].search(domain)
            won = leads.filtered(lambda l: l.stage_id.is_won)
            rec.revenue_achieved = sum(l.expected_revenue or 0.0 for l in won)
            rec.deals_achieved = len(won)
            rec.leads_generated = len(leads)

    @api.depends("revenue_target", "revenue_achieved", "deals_target", "deals_achieved",
                 "leads_target", "leads_generated")
    def _compute_progress(self):
        for rec in self:
            rec.revenue_progress = (
                (rec.revenue_achieved / rec.revenue_target * 100)
                if rec.revenue_target else 0.0
            )
            rec.deals_progress = (
                (rec.deals_achieved / rec.deals_target * 100)
                if rec.deals_target else 0.0
            )
            rec.leads_progress = (
                (rec.leads_generated / rec.leads_target * 100)
                if rec.leads_target else 0.0
            )
