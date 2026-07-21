from odoo import api, fields, models, _


class TenderAlert(models.Model):
    _name = 'tender.alert'
    _description = 'Tender Alert'
    _order = 'alert_date desc'

    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    alert_type = fields.Selection([
        ('deadline_approaching', 'Deadline Approaching'),
        ('deadline_overdue', 'Deadline Overdue'),
        ('stage_change', 'Stage Change'),
        ('result_pending', 'Result Pending'),
        ('site_visit', 'Site Visit Reminder'),
        ('bid_bond_expiry', 'Bid Bond Expiry'),
        ('custom', 'Custom Reminder'),
    ], string='Alert Type', required=True)
    alert_date = fields.Datetime(string='Alert Date', default=fields.Datetime.now)
    triggered = fields.Boolean(string='Triggered', default=False)
    notified_partner_ids = fields.Many2many('res.users', string='Notified Users')
    message = fields.Text(string='Message', required=True)

    def action_trigger(self):
        for alert in self:
            if alert.triggered:
                continue
            tender = alert.tender_id
            for user in tender.team_ids | tender.user_id:
                alert._notify_user(user)
            alert.triggered = True

    def _notify_user(self, user):
        self.tender_id.message_post(
            body=self.message,
            partner_ids=[user.partner_id.id],
            subject=_('Tender Alert: %s', self.tender_id.display_name),
        )

    @api.model
    def _cron_check_deadlines(self):
        now = fields.Datetime.now()
        Tender = self.env['tender.tender']

        approaching = Tender.search([
            ('deadline_submission', '>', now),
            ('deadline_submission', '<=', now.replace(hour=23, minute=59, second=59) + fields.Date.to_datetime(fields.Date.context_today(self).replace(day=fields.Date.context_today(self).day + 3)) if False else now),
        ])
        self._create_deadline_alerts(approaching, 'deadline_approaching',
                                     'Deadline approaching: %s')

        overdue = Tender.search([
            ('deadline_submission', '<', now),
            ('result', '=', False),
        ])
        self._create_deadline_alerts(overdue, 'deadline_overdue',
                                     'Submission deadline has passed: %s')

    def _create_deadline_alerts(self, tenders, alert_type, msg_template):
        for t in tenders:
            existing = self.search([
                ('tender_id', '=', t.id),
                ('alert_type', '=', alert_type),
                ('triggered', '=', False),
            ], limit=1)
            if existing:
                continue
            self.create({
                'tender_id': t.id,
                'alert_type': alert_type,
                'message': msg_template % t.display_name,
            })
