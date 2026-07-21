from odoo import api, fields, models, _


class MarketingAutomation(models.Model):
    _name = 'marketing.automation'
    _description = 'Marketing Automation Rule'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'create_date DESC'

    name = fields.Char('Rule Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    model_id = fields.Many2one(
        'ir.model', string='Trigger Model',
        required=True, ondelete='cascade',
        domain=[('is_mailing_enabled', '=', True)])
    model_name = fields.Char(
        string='Model Name',
        related='model_id.model', readonly=True, store=True)

    trigger_event = fields.Selection([
        ('create', 'Record Created'),
        ('write', 'Record Updated'),
        ('stage_change', 'Stage Changed'),
        ('email_opened', 'Email Opened'),
        ('email_clicked', 'Email Clicked'),
        ('email_bounced', 'Email Bounced'),
        ('form_submitted', 'Form Submitted'),
        ('lead_won', 'Lead Won'),
        ('lead_lost', 'Lead Lost'),
        ('date_reached', 'Date Reached'),
    ], string='Trigger Event', required=True, default='create')

    trigger_field_id = fields.Many2one(
        'ir.model.fields', string='Trigger Field',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['many2one', 'selection', 'date', 'datetime'])]")

    trigger_stage_id = fields.Many2one(
        'crm.stage', string='Trigger Stage')
    trigger_field_value = fields.Char('Trigger Field Value')

    trigger_date_field_id = fields.Many2one(
        'ir.model.fields', string='Date Field',
        domain="[('model_id', '=', model_id), ('ttype', 'in', ['date', 'datetime'])]")
    trigger_delay_days = fields.Integer('Delay (Days)', default=0)

    domain = fields.Char('Target Domain', default='[]',
                         help='Domain to filter which records trigger this rule.')

    action_ids = fields.One2many(
        'marketing.automation.action', 'automation_id',
        string='Actions', copy=True)

    execution_count = fields.Integer('Total Executions', readonly=True)
    last_execution = fields.Datetime('Last Execution', readonly=True)
    success_count = fields.Integer('Successful Executions', readonly=True)
    failed_count = fields.Integer('Failed Executions', readonly=True)

    def action_activate(self):
        self.write({'active': True})

    def action_deactivate(self):
        self.write({'active': False})

    def _evaluate_domain(self, record):
        if not self.domain or self.domain == '[]':
            return True
        try:
            domain = eval(self.domain)
            return record.filtered_domain(domain)
        except Exception:
            return False

    def _execute_actions(self, record):
        self.ensure_one()
        for action in self.action_ids.filtered(lambda a: a.active):
            try:
                action._execute(record)
                self.success_count += 1
            except Exception:
                self.failed_count += 1
        self.execution_count += 1
        self.last_execution = fields.Datetime.now()

    @api.model
    def _process_automation_rules(self, model_name, res_id, event):
        rules = self.search([
            ('active', '=', True),
            ('model_name', '=', model_name),
            ('trigger_event', '=', event),
        ])
        for rule in rules:
            record = self.env[model_name].browse(res_id)
            if record and rule._evaluate_domain(record):
                rule._execute_actions(record)

    @api.model
    def _cron_process_date_automations(self):
        today = fields.Date.today()
        rules = self.search([
            ('active', '=', True),
            ('trigger_event', '=', 'date_reached'),
            ('trigger_date_field_id', '!=', False),
        ])
        for rule in rules:
            field_name = rule.trigger_date_field_id.name
            model = self.env[rule.model_name]
            records = model.search([
                (field_name, '=', today),
            ])
            for record in records:
                if rule._evaluate_domain(record):
                    rule._execute_actions(record)
