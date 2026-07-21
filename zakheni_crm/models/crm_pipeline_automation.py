from odoo import api, fields, models


class PipelineAutomation(models.Model):
    _name = "crm.pipeline.automation"
    _description = "Pipeline Automation Rule"
    _rec_name = "name"
    _order = "sequence, id"

    name = fields.Char("Rule Name", required=True)
    active = fields.Boolean("Active", default=True)
    sequence = fields.Integer("Sequence", default=10)
    model = fields.Selection([
        ("crm.lead", "Lead/Opportunity"),
    ], string="Model", default="crm.lead", required=True)
    trigger = fields.Selection([
        ("stage_entered", "Stage Entered"),
        ("stage_exited", "Stage Exited"),
        ("lead_created", "Lead Created"),
        ("lead_won", "Lead Won"),
        ("lead_lost", "Lead Lost"),
        ("score_threshold", "Score Threshold Reached"),
        ("sla_breach", "SLA Breached"),
    ], string="Trigger", required=True)
    trigger_stage_id = fields.Many2one("crm.stage", string="Trigger Stage",
        help="Required when trigger is Stage Entered/Exited")
    score_threshold = fields.Integer("Score Threshold",
        help="Required when trigger is Score Threshold Reached")
    action_type = fields.Selection([
        ("email", "Send Email"),
        ("activity", "Create Activity"),
        ("move_stage", "Move to Stage"),
        ("assign_user", "Assign User"),
        ("update_field", "Update Field"),
        ("add_tag", "Add Tag"),
        ("webhook", "Call Webhook"),
    ], string="Action Type", required=True)
    target_stage_id = fields.Many2one("crm.stage", string="Target Stage")
    email_template_id = fields.Many2one("mail.template", string="Email Template")
    activity_type_id = fields.Many2one("mail.activity.type", string="Activity Type")
    activity_summary = fields.Char("Activity Summary")
    activity_date_deadline = fields.Integer("Activity Due (Days)", default=1)
    user_id = fields.Many2one("res.users", string="Assign User")
    field_name = fields.Char("Field Name (Technical)")
    field_value = fields.Char("Field Value")
    tag_ids = fields.Many2many("crm.tag", string="Tags to Add")
    webhook_url = fields.Char("Webhook URL")

    @api.model
    def _evaluate_triggers(self, lead, trigger, extra=None):
        rules = self.search([("active", "=", True), ("trigger", "=", trigger)])
        for rule in rules:
            if trigger in ("stage_entered", "stage_exited"):
                extra_stage = extra.get("stage_id") if extra else False
                if rule.trigger_stage_id and extra_stage and rule.trigger_stage_id.id != extra_stage.id:
                    continue
            if trigger == "score_threshold":
                if lead.total_score < rule.score_threshold:
                    continue
            if trigger == "sla_breach":
                if lead.sla_id and lead.sla_status != "breached":
                    continue
            rule._execute_action(lead)

    def _execute_action(self, lead):
        self.ensure_one()
        if self.action_type == "move_stage" and self.target_stage_id:
            lead.stage_id = self.target_stage_id
        elif self.action_type == "assign_user" and self.user_id:
            lead.user_id = self.user_id
        elif self.action_type == "email" and self.email_template_id:
            lead.message_post_with_template(self.email_template_id.id)
        elif self.action_type == "activity" and self.activity_type_id:
            lead.activity_schedule(
                self.activity_type_id.id,
                summary=self.activity_summary or self.name,
                date_deadline=fields.Date.today() if self.activity_date_deadline == 0
                    else fields.Date.add(fields.Date.today(), days=self.activity_date_deadline),
            )
        elif self.action_type == "add_tag" and self.tag_ids:
            lead.write({"tag_ids": [(4, tag.id) for tag in self.tag_ids]})
