from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    lead_grade_id = fields.Many2one("crm.lead.grade", string="Lead Grade", tracking=True)
    total_score = fields.Integer("Total Score", compute="_compute_total_score", store=True)
    score_ids = fields.One2many("crm.lead.score", "lead_id", string="Score History")
    score_count = fields.Integer("Score Entries", compute="_compute_score_count")
    competitor_id = fields.Many2one("crm.competitor", string="Competitor", tracking=True)
    territory_id = fields.Many2one("crm.territory", string="Territory", tracking=True)
    sla_id = fields.Many2one("crm.sla", string="SLA Policy")
    sla_deadline = fields.Datetime("SLA Deadline", compute="_compute_sla_deadline", store=True, tracking=True)
    sla_status = fields.Selection([
        ("on_track", "On Track"),
        ("at_risk", "At Risk"),
        ("breached", "Breached"),
    ], string="SLA Status", compute="_compute_sla_status", store=True)
    is_in_sequence = fields.Boolean("In Email Sequence", default=False)
    email_sequence_id = fields.Many2one("crm.email.sequence", string="Email Sequence")
    sequence_step = fields.Integer("Sequence Step", default=0)
    next_sequence_date = fields.Datetime("Next Sequence Email")
    forecast_amount = fields.Monetary("Forecast Amount", currency_field="company_currency", compute="_compute_forecast_amount", store=True)
    forecast_model = fields.Selection([
        ("optimistic", "Optimistic"),
        ("pessimistic", "Pessimistic"),
        ("most_likely", "Most Likely"),
    ], string="Forecast Model", default="most_likely")
    win_probability_adjusted = fields.Float("Adjusted Probability", compute="_compute_win_probability_adjusted", store=True)

    @api.depends("score_ids.score")
    def _compute_total_score(self):
        for lead in self:
            lead.total_score = sum(lead.score_ids.mapped("score")) if lead.score_ids else 0

    def _compute_score_count(self):
        for lead in self:
            lead.score_count = len(lead.score_ids)

    @api.depends("probability", "total_score", "lead_grade_id")
    def _compute_win_probability_adjusted(self):
        for lead in self:
            score_factor = min(lead.total_score / 100.0, 0.5) if lead.total_score else 0.0
            base_prob = lead.probability or 0.0
            adjusted = base_prob + (score_factor * (100.0 - base_prob))
            lead.win_probability_adjusted = round(min(adjusted, 99.0), 1)

    @api.depends("sla_id", "sla_id.hours", "create_date")
    def _compute_sla_deadline(self):
        for lead in self:
            if lead.sla_id and lead.create_date:
                lead.sla_deadline = lead.sla_id._compute_deadline(lead.create_date)
            else:
                lead.sla_deadline = False

    @api.depends("sla_deadline")
    def _compute_sla_status(self):
        now = fields.Datetime.now()
        for lead in self:
            if not lead.sla_deadline:
                lead.sla_status = False
            elif lead.sla_deadline < now:
                lead.sla_status = "breached"
            elif lead.sla_deadline:
                lead.sla_status = "on_track"

    @api.depends("expected_revenue", "probability", "win_probability_adjusted")
    def _compute_forecast_amount(self):
        for lead in self:
            adj_prob = lead.win_probability_adjusted / 100.0 if lead.win_probability_adjusted else (lead.probability or 0.0) / 100.0
            lead.forecast_amount = lead.expected_revenue * adj_prob if lead.expected_revenue else 0.0

    def action_set_won(self):
        res = super().action_set_won()
        for lead in self:
            if lead.sla_id and lead.sla_deadline and fields.Datetime.now() <= lead.sla_deadline:
                lead.sla_id._add_sla_success()
        return res

    def _score_lead_automatically(self):
        for lead in self:
            rules = self.env["crm.scoring.rule"].search([("active", "=", True)])
            for rule in rules:
                score = rule._evaluate(lead)
                if score:
                    self.env["crm.lead.score"].create({
                        "lead_id": lead.id,
                        "rule_id": rule.id,
                        "score": score,
                    })
            grades = self.env["crm.lead.grade"].search([("active", "=", True)]).sorted("min_score", reverse=True)
            for grade in grades:
                if lead.total_score >= grade.min_score:
                    lead.lead_grade_id = grade
                    break

    @api.model
    def _cron_score_all_leads(self):
        leads = self.search([("active", "=", True)])
        for lead in leads:
            lead.score_ids.unlink()
            lead._score_lead_automatically()

    def action_recalculate_score(self):
        self.score_ids.unlink()
        self._score_lead_automatically()

    @api.model
    def _cron_check_sla_breaches(self):
        now = fields.Datetime.now()
        leads = self.search([
            ("sla_id", "!=", False),
            ("sla_deadline", "<", now),
            ("sla_status", "!=", "breached"),
            ("active", "=", True),
        ])
        for lead in leads:
            lead.sla_status = "breached"
            if lead.sla_id:
                lead.sla_id._add_sla_breach()
            self.env["crm.pipeline.automation"]._evaluate_triggers(
                lead, "sla_breach"
            )
