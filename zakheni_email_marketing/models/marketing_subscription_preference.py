from odoo import api, fields, models


class MarketingSubscriptionPreference(models.Model):
    _name = 'marketing.subscription.preference'
    _description = 'Marketing Subscription Preference'
    _rec_name = 'contact_id'
    _order = 'create_date DESC'

    contact_id = fields.Many2one(
        'mailing.contact', string='Contact',
        required=True, ondelete='cascade')
    partner_id = fields.Many2one(
        'res.partner', string='Partner',
        ondelete='cascade')
    list_id = fields.Many2one(
        'mailing.list', string='Mailing List',
        required=True, ondelete='cascade')

    subscription_status = fields.Selection([
        ('subscribed', 'Subscribed'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('complained', 'Complained'),
    ], string='Status', default='subscribed', required=True)

    subscribed_date = fields.Datetime('Subscribed Date', default=fields.Datetime.now)
    unsubscribed_date = fields.Datetime('Unsubscribed Date')
    unsubscribed_reason = fields.Selection([
        ('manual', 'Manually Unsubscribed'),
        ('bounced', 'Email Bounced'),
        ('complaint', 'Spam Complaint'),
        ('link', 'Unsubscribe Link'),
        ('inactive', 'Inactive / Auto Cleanup'),
    ], string='Unsubscribe Reason')

    communication_channel = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Both Email & SMS'),
    ], string='Preferred Channel', default='both')

    email_frequency = fields.Selection([
        ('immediate', 'Immediate'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
        ('monthly', 'Monthly Digest'),
        ('never', 'Never'),
    ], string='Email Frequency', default='immediate')

    tags = fields.Char('Interest Tags',
                       help='Comma-separated list of interest tags')

    consent_given = fields.Boolean('Consent Given', default=True)
    consent_date = fields.Datetime('Consent Date')
    consent_source = fields.Char('Consent Source')

    def action_subscribe(self):
        self.write({
            'subscription_status': 'subscribed',
            'subscribed_date': fields.Datetime.now(),
            'unsubscribed_date': False,
            'unsubscribed_reason': False,
        })

    def action_unsubscribe(self, reason='manual'):
        self.write({
            'subscription_status': 'unsubscribed',
            'unsubscribed_date': fields.Datetime.now(),
            'unsubscribed_reason': reason,
        })
