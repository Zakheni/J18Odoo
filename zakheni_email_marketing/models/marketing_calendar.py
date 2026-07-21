from odoo import api, fields, models, _


class MarketingCalendar(models.Model):
    _name = 'marketing.calendar'
    _description = 'Marketing Calendar'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'start_date DESC'

    name = fields.Char('Event Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)

    event_type = fields.Selection([
        ('campaign_start', 'Campaign Start'),
        ('campaign_end', 'Campaign End'),
        ('mailing_send', 'Email Mailing'),
        ('sms_send', 'SMS Mailing'),
        ('automation', 'Automation Trigger'),
        ('ab_test', 'A/B Test Evaluation'),
        ('segment_sync', 'Segment Sync'),
        ('report', 'Reporting Period'),
        ('review', 'Campaign Review'),
        ('holiday', 'Holiday / Blackout'),
        ('other', 'Other'),
    ], string='Event Type', required=True)

    start_date = fields.Datetime('Start Date', required=True)
    end_date = fields.Datetime('End Date')
    duration = fields.Float(
        'Duration (Hours)',
        compute='_compute_duration', store=True)
    all_day = fields.Boolean('All Day')

    color = fields.Integer('Color')
    description = fields.Text('Description')

    campaign_id = fields.Many2one(
        'marketing.campaign', string='Campaign',
        ondelete='cascade')
    mailing_id = fields.Many2one(
        'mailing.mailing', string='Mailing',
        ondelete='set null')
    automation_id = fields.Many2one(
        'marketing.automation', string='Automation Rule',
        ondelete='set null')

    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user)
    team_id = fields.Many2one(
        'crm.team', string='Team')

    recurring = fields.Boolean('Recurring Event')
    recurring_interval = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ], string='Recurrence', default='weekly')

    completed = fields.Boolean('Completed', default=False)
    completion_date = fields.Datetime('Completion Date')

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for event in self:
            if event.start_date and event.end_date:
                delta = event.end_date - event.start_date
                event.duration = delta.total_seconds() / 3600.0
            else:
                event.duration = 0.0

    def action_mark_completed(self):
        self.write({
            'completed': True,
            'completion_date': fields.Datetime.now(),
        })

    def action_reopen(self):
        self.write({'completed': False, 'completion_date': False})

    @api.model
    def get_calendar_events(self, start_date, end_date):
        events = self.search([
            ('start_date', '<=', end_date),
            '|',
            ('end_date', '>=', start_date),
            ('start_date', '>=', start_date),
        ])
        return events
