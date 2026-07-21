from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class MarketingCampaignStep(models.Model):
    _name = 'marketing.campaign.step'
    _description = 'Marketing Campaign Step'
    _rec_name = 'name'
    _order = 'sequence, id'

    name = fields.Char('Step Name', required=True)
    campaign_id = fields.Many2one(
        'marketing.campaign', string='Campaign',
        required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    trigger_type = fields.Selection([
        ('immediate', 'Immediate (Start of Campaign)'),
        ('scheduled', 'Scheduled (Date/Time)'),
        ('delay_after_previous', 'Delay After Previous Step'),
        ('event_based', 'Event-Based Trigger'),
        ('behavior_based', 'Behavior-Based Trigger'),
    ], string='Trigger Type', default='immediate', required=True)

    delay_days = fields.Integer('Delay (Days)')
    delay_hours = fields.Integer('Delay (Hours)')
    scheduled_date = fields.Datetime('Scheduled Date')

    mailing_template_id = fields.Many2one(
        'mailing.mailing', string='Email Template',
        domain=[('state', '=', 'draft')])
    sms_template_id = fields.Many2one(
        'sms.sms', string='SMS Template')

    mailing_type = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both Email & SMS'),
    ], string='Mailing Type', default='email', required=True)

    condition_domain = fields.Char(
        'Recipient Condition Domain',
        default='[]',
        help='Domain expression to filter recipients for this step.')
    condition_model = fields.Char(
        'Condition Model',
        default='mailing.contact')

    mail_server_id = fields.Many2one(
        'ir.mail_server', string='Mail Server')

    segment_ids = fields.Many2many(
        'marketing.segment', string='Filter Segments')

    action_type = fields.Selection([
        ('send_mail', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('update_lead_score', 'Update Lead Score'),
        ('add_to_segment', 'Add to Segment'),
        ('remove_from_segment', 'Remove from Segment'),
        ('create_task', 'Create Task for Sales Team'),
        ('create_lead', 'Create Lead/Opportunity'),
        ('webhook', 'Call Webhook'),
    ], string='Action Type', default='send_mail', required=True)

    lead_score_change = fields.Integer(
        'Lead Score Change',
        help='Positive or negative score change')

    target_segment_id = fields.Many2one(
        'marketing.segment', string='Target Segment')

    webhook_url = fields.Char('Webhook URL')
    webhook_method = fields.Selection([
        ('POST', 'POST'),
        ('GET', 'GET'),
    ], string='Webhook Method', default='POST')

    task_title = fields.Char('Task Title')
    task_description = fields.Text('Task Description')
    task_user_id = fields.Many2one('res.users', string='Assign Task To')
    task_team_id = fields.Many2one('crm.team', string='Sales Team')

    lead_team_id = fields.Many2one('crm.team', string='Lead Team')
    lead_user_id = fields.Many2one('res.users', string='Lead Responsible')

    executed_count = fields.Integer('Times Executed', readonly=True)
    last_execution = fields.Datetime('Last Execution', readonly=True)
    success_count = fields.Integer('Successful Executions', readonly=True)

    @api.constrains('trigger_type', 'delay_days', 'scheduled_date')
    def _check_trigger_config(self):
        for step in self:
            if step.trigger_type == 'delay_after_previous' and not step.delay_days and not step.delay_hours:
                raise ValidationError(_('Please set a delay duration for this step.'))
            if step.trigger_type == 'scheduled' and not step.scheduled_date:
                raise ValidationError(_('Please set a scheduled date for this step.'))

    def _execute_step(self):
        self.ensure_one()
        if self.action_type == 'send_mail' and self.mailing_template_id:
            mailing = self.mailing_template_id
            if self.mail_server_id:
                mailing.mail_server_id = self.mail_server_id
            if self.segment_ids:
                contacts = self.env['mailing.contact']
                for segment in self.segment_ids:
                    contacts |= segment._get_contacts()
                if contacts:
                    mailing.write({
                        'contact_list_ids': [(4, lst.id) for lst in contacts.mapped('list_ids')],
                    })
            mailing.action_put_in_queue()
            self.executed_count += 1
            self.success_count += 1
            self.last_execution = fields.Datetime.now()
        elif self.action_type == 'update_lead_score':
            self._execute_update_score()
        elif self.action_type == 'add_to_segment':
            self._execute_add_to_segment()
        elif self.action_type == 'create_lead':
            self._execute_create_lead()
        elif self.action_type == 'webhook':
            self._execute_webhook()

    def _execute_update_score(self):
        if self.target_segment_id and self.lead_score_change:
            contacts = self.target_segment_id._get_contacts()
            for contact in contacts:
                lead = self.env['crm.lead'].search([
                    ('email_from', '=', contact.email),
                    ('active', '=', True),
                ], limit=1)
                if lead:
                    score = lead.zakheni_lead_score or 0
                    lead.zakheni_lead_score = max(0, score + self.lead_score_change)
            self.executed_count += 1
            self.success_count += 1

    def _execute_add_to_segment(self):
        if self.target_segment_id:
            self.executed_count += 1
            self.success_count += 1

    def _execute_create_lead(self):
        if self.lead_team_id:
            contacts = self.env['mailing.contact']
            if self.segment_ids:
                for segment in self.segment_ids:
                    contacts |= segment._get_contacts()
            for contact in contacts:
                self.env['crm.lead'].create({
                    'name': _('Campaign Lead: %s') % contact.name,
                    'partner_name': contact.name,
                    'email_from': contact.email,
                    'team_id': self.lead_team_id.id,
                    'user_id': self.lead_user_id.id or self.lead_team_id.user_id.id,
                    'campaign_id': self.campaign_id.utm_campaign_id.id,
                })
                self.success_count += 1
            self.executed_count += 1

    def _execute_webhook(self):
        if self.webhook_url:
            try:
                import requests
                requests.request(
                    method=self.webhook_method,
                    url=self.webhook_url,
                    timeout=10,
                )
                self.success_count += 1
            except Exception:
                pass
            self.executed_count += 1
            self.last_execution = fields.Datetime.now()
