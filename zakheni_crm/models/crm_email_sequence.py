from odoo import api, fields, models


class EmailSequence(models.Model):
    _name = "crm.email.sequence"
    _description = "CRM Email Sequence"
    _rec_name = "name"
    _order = "name"

    name = fields.Char("Sequence Name", required=True)
    active = fields.Boolean("Active", default=True)
    model = fields.Selection([
        ("crm.lead", "Lead/Opportunity"),
    ], string="Apply On", default="crm.lead", required=True)
    trigger = fields.Selection([
        ("lead_created", "Lead Created"),
        ("stage_entered", "Stage Entered"),
        ("lead_won", "Lead Won"),
    ], string="Trigger", default="lead_created", required=True)
    trigger_stage_id = fields.Many2one("crm.stage", string="Trigger Stage")
    step_ids = fields.One2many("crm.email.sequence.step", "sequence_id", string="Steps",
        copy=True)
    lead_ids = fields.One2many("crm.lead", "email_sequence_id", string="Leads")
    lead_count = fields.Integer("Active Leads", compute="_compute_lead_count")

    def _compute_lead_count(self):
        lead_data = self.env["crm.lead"]._read_group(
            [("email_sequence_id", "in", self.ids), ("active", "=", True)],
            ["email_sequence_id"],
            ["__count"],
        )
        counts = {item["email_sequence_id"][0]: item["__count"] for item in lead_data if item["email_sequence_id"]}
        for seq in self:
            seq.lead_count = counts.get(seq.id, 0)

    def _enroll_lead(self, lead):
        self.ensure_one()
        lead.email_sequence_id = self
        lead.is_in_sequence = True
        lead.sequence_step = 0
        lead.next_sequence_date = fields.Datetime.now()
        self._send_step(lead, 0)

    def _send_step(self, lead, step_index):
        self.ensure_one()
        steps = self.step_ids.sorted("sequence")
        if step_index >= len(steps):
            lead.is_in_sequence = False
            return
        step = steps[step_index]
        template = step.email_template_id
        if template:
            lead.message_post_with_template(template.id)
        lead.sequence_step = step_index + 1
        if lead.sequence_step < len(steps):
            next_step = steps[lead.sequence_step]
            lead.next_sequence_date = fields.Datetime.add(
                fields.Datetime.now(), days=next_step.delay_days
            )
        else:
            lead.is_in_sequence = False
            lead.next_sequence_date = False

    @api.model
    def _cron_process_sequences(self):
        now = fields.Datetime.now()
        leads = self.env["crm.lead"].search([
            ("is_in_sequence", "=", True),
            ("next_sequence_date", "<=", now),
            ("active", "=", True),
        ])
        for lead in leads:
            if lead.email_sequence_id:
                lead.email_sequence_id._send_step(lead, lead.sequence_step)


class EmailSequenceStep(models.Model):
    _name = "crm.email.sequence.step"
    _description = "Email Sequence Step"
    _rec_name = "subject"
    _order = "sequence, id"

    sequence_id = fields.Many2one("crm.email.sequence", string="Sequence", required=True, ondelete="cascade")
    sequence = fields.Integer("Sequence", default=10)
    delay_days = fields.Integer("Delay (Days)", default=1, required=True)
    email_template_id = fields.Many2one("mail.template", string="Email Template")
    subject = fields.Char("Subject", compute="_compute_subject", store=True)

    @api.depends("email_template_id", "email_template_id.subject")
    def _compute_subject(self):
        for step in self:
            step.subject = step.email_template_id.subject if step.email_template_id else "No template"
