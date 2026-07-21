from odoo import api, fields, models, _


class MarketingAutomationAction(models.Model):
    _name = 'marketing.automation.action'
    _description = 'Marketing Automation Action'
    _rec_name = 'name'
    _order = 'sequence, id'

    name = fields.Char('Action Name', required=True)
    automation_id = fields.Many2one(
        'marketing.automation', string='Automation Rule',
        required=True, ondelete='cascade')
    sequence = fields.Integer('Sequence', default=10)
    active = fields.Boolean('Active', default=True)

    action_type = fields.Selection([
        ('send_email', 'Send Email'),
        ('send_sms', 'Send SMS'),
        ('add_to_list', 'Add to Mailing List'),
        ('remove_from_list', 'Remove from Mailing List'),
        ('update_contact', 'Update Contact Field'),
        ('create_lead', 'Create Lead/Opportunity'),
        ('update_lead', 'Update Lead'),
        ('change_stage', 'Change Stage'),
        ('assign_user', 'Assign to User'),
        ('add_tag', 'Add Tag'),
        ('notify_user', 'Notify User'),
        ('webhook', 'Call Webhook'),
    ], string='Action Type', default='send_email', required=True)

    mailing_id = fields.Many2one(
        'mailing.mailing', string='Email Template')
    mailing_list_id = fields.Many2one(
        'mailing.list', string='Mailing List')
    sms_template_id = fields.Many2one(
        'sms.sms', string='SMS Template')

    update_field_id = fields.Many2one(
        'ir.model.fields', string='Field to Update',
        domain="[('model_id.model', '=', automation_id.model_name)]")
    update_value = fields.Char('Field Value')

    lead_team_id = fields.Many2one(
        'crm.team', string='Sales Team')
    lead_user_id = fields.Many2one(
        'res.users', string='Responsible')
    stage_id = fields.Many2one(
        'crm.stage', string='Stage')
    tag_ids = fields.Many2many(
        'crm.tag', string='Tags')

    user_id = fields.Many2one(
        'res.users', string='Notify User')

    webhook_url = fields.Char('Webhook URL')
    webhook_method = fields.Selection([
        ('POST', 'POST'),
        ('GET', 'GET'),
    ], string='Webhook Method', default='POST')

    execution_count = fields.Integer('Executions', readonly=True)
    last_execution = fields.Datetime('Last Execution', readonly=True)

    def _execute(self, record):
        self.ensure_one()
        if self.action_type == 'send_email' and self.mailing_id:
            if hasattr(record, 'email') and record.email:
                self.mailing_id.with_context(
                    force_email=record.email
                ).action_put_in_queue()

        elif self.action_type == 'add_to_list' and self.mailing_list_id:
            if hasattr(record, 'email') and record.email:
                contact = self.env['mailing.contact'].search([
                    ('email', '=', record.email),
                ], limit=1)
                if contact:
                    contact.write({'list_ids': [(4, self.mailing_list_id.id)]})

        elif self.action_type == 'remove_from_list' and self.mailing_list_id:
            if hasattr(record, 'email') and record.email:
                contact = self.env['mailing.contact'].search([
                    ('email', '=', record.email),
                ], limit=1)
                if contact:
                    contact.write({'list_ids': [(3, self.mailing_list_id.id)]})

        elif self.action_type == 'create_lead':
            lead_vals = {
                'name': _('Automation Lead: %s') % (record.display_name or 'Unknown'),
            }
            if hasattr(record, 'email_from'):
                lead_vals['email_from'] = record.email_from
            if hasattr(record, 'partner_name'):
                lead_vals['partner_name'] = record.partner_name
            if self.lead_team_id:
                lead_vals['team_id'] = self.lead_team_id.id
            if self.lead_user_id:
                lead_vals['user_id'] = self.lead_user_id.id
            if self.stage_id:
                lead_vals['stage_id'] = self.stage_id.id
            self.env['crm.lead'].create(lead_vals)

        elif self.action_type == 'change_stage' and self.stage_id:
            if hasattr(record, 'stage_id'):
                record.stage_id = self.stage_id

        elif self.action_type == 'assign_user' and self.user_id:
            if hasattr(record, 'user_id'):
                record.user_id = self.user_id

        elif self.action_type == 'add_tag' and self.tag_ids:
            if hasattr(record, 'tag_ids'):
                record.tag_ids = [(4, tag.id, 0) for tag in self.tag_ids]

        elif self.action_type == 'notify_user' and self.user_id:
            record._message_log(
                body=_('Automation notification for %s') % record.display_name,
                partner_ids=[self.user_id.partner_id.id],
            )

        elif self.action_type == 'webhook' and self.webhook_url:
            try:
                import requests
                requests.request(
                    method=self.webhook_method,
                    url=self.webhook_url,
                    json={'record_id': record.id, 'model': record._name},
                    timeout=10,
                )
            except Exception:
                pass

        self.execution_count += 1
        self.last_execution = fields.Datetime.now()
