from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class MarketingReengagement(models.Model):
    _name = 'marketing.reengagement'
    _description = 'Re-engagement Campaign'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'create_date DESC'

    name = fields.Char('Campaign Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)

    inactivity_days = fields.Integer(
        'Inactivity Period (Days)', required=True, default=90,
        help='Number of days of inactivity before triggering re-engagement.')
    max_attempts = fields.Integer(
        'Max Attempts', default=3,
        help='Maximum number of re-engagement emails to send.')

    trigger_event = fields.Selection([
        ('no_open', 'No Email Open'),
        ('no_click', 'No Link Click'),
        ('no_purchase', 'No Purchase'),
        ('no_visit', 'No Website Visit'),
    ], string='Trigger Condition', default='no_open', required=True)

    segment_id = fields.Many2one(
        'marketing.segment', string='Target Segment',
        required=True,
        help='Segment of contacts to target for re-engagement.')

    email_template_ids = fields.One2many(
        'mailing.mailing', 'reengagement_id',
        string='Re-engagement Emails')
    winback_mailing_id = fields.Many2one(
        'mailing.mailing', string='Win-back Email',
        domain=[('state', '=', 'draft')],
        help='Final offer email before removing from list.')

    action_on_failure = fields.Selection([
        ('remove_from_list', 'Remove from Mailing List'),
        ('archive_contact', 'Archive Contact'),
        ('mark_inactive', 'Mark as Inactive'),
        ('reduce_frequency', 'Reduce Email Frequency'),
    ], string='Action on Failure', default='reduce_frequency')

    target_list_ids = fields.Many2many(
        'mailing.list', string='Target Lists')

    success_count = fields.Integer('Re-engaged Contacts', readonly=True)
    lost_count = fields.Integer('Lost Contacts', readonly=True)
    last_run = fields.Datetime('Last Run', readonly=True)

    @api.model
    def _cron_process_reengagement(self):
        campaigns = self.search([('active', '=', True)])
        for campaign in campaigns:
            campaign._process_reengagement()

    def _process_reengagement(self):
        self.ensure_one()
        contacts = self.segment_id._get_contacts()
        cutoff = fields.Datetime.now() - relativedelta(days=self.inactivity_days)
        for contact in contacts:
            if self.trigger_event == 'no_open':
                if contact.last_open_date and contact.last_open_date > cutoff:
                    continue
                if not contact.last_open_date and contact.create_date > cutoff:
                    continue
            elif self.trigger_event == 'no_click':
                if contact.last_click_date and contact.last_click_date > cutoff:
                    continue
            target_lists = self.target_list_ids or contact.list_ids
            for lst in target_lists:
                pref = self.env['marketing.subscription.preference'].search([
                    ('contact_id', '=', contact.id),
                    ('list_id', '=', lst.id),
                ], limit=1)
                if pref and pref.subscription_status == 'unsubscribed':
                    continue
            if self.winback_mailing_id and self.max_attempts > 0:
                mailing = self.winback_mailing_id.copy({
                    'contact_list_ids': [(4, lst.id) for lst in target_lists],
                })
                mailing.action_put_in_queue()
                self.success_count += 1
        self.last_run = fields.Datetime.now()

    def action_run_now(self):
        self._process_reengagement()
