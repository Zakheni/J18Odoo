from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    zakheni_lead_score = fields.Integer(
        'Lead Score', default=0,
        help='Score based on email engagement and behavior.')
    zakheni_last_email_open = fields.Datetime('Last Email Open')
    zakheni_last_email_click = fields.Datetime('Last Email Click')
    zakheni_email_opens = fields.Integer('Total Email Opens', default=0)
    zakheni_email_clicks = fields.Integer('Total Email Clicks', default=0)
    zakheni_email_replies = fields.Integer('Total Email Replies', default=0)
    zakheni_score_history = fields.Text('Score Change History')

    def _update_score_from_trace(self, trace):
        self.ensure_one()
        changes = []
        if trace.trace_status == 'open':
            self.zakheni_email_opens += 1
            self.zakheni_last_email_open = fields.Datetime.now()
            changes.append(('+5', 'Email opened'))
            self.zakheni_lead_score += 5
        elif trace.trace_status == 'reply':
            self.zakheni_email_replies += 1
            changes.append(('+15', 'Email replied'))
            self.zakheni_lead_score += 15
        if trace.links_click_ids:
            self.zakheni_email_clicks += len(trace.links_click_ids)
            self.zakheni_last_email_click = fields.Datetime.now()
            changes.append(('+10', 'Link clicked'))
            self.zakheni_lead_score += 10 * len(trace.links_click_ids)


class MarketingLeadScore(models.Model):
    _name = 'marketing.lead.score'
    _description = 'Marketing Lead Scoring Rule'
    _rec_name = 'name'
    _order = 'sequence, id'

    name = fields.Char('Rule Name', required=True)
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)

    campaign_id = fields.Many2one(
        'marketing.campaign', string='Campaign',
        ondelete='cascade')

    trigger_event = fields.Selection([
        ('email_opened', 'Email Opened'),
        ('email_clicked', 'Link Clicked'),
        ('email_replied', 'Email Replied'),
        ('email_bounced', 'Email Bounced'),
        ('form_submitted', 'Form Submitted'),
        ('landing_page_visited', 'Landing Page Visited'),
        ('purchase_made', 'Purchase Made'),
        ('unsubscribed', 'Unsubscribed'),
    ], string='Trigger Event', required=True)

    score_change = fields.Integer(
        'Score Change', required=True, default=5,
        help='Positive or negative score change.')
    max_score = fields.Integer(
        'Maximum Score',
        help='Maximum score this rule can contribute.')

    mailing_id = fields.Many2one(
        'mailing.mailing', string='Specific Mailing',
        help='Only apply to this mailing.')
    mailing_model_id = fields.Many2one(
        'ir.model', string='Target Model',
        domain=[('is_mailing_enabled', '=', True)])
    domain = fields.Char(
        'Target Domain', default='[]')

    description = fields.Text('Description')
    current_count = fields.Integer('Times Applied', readonly=True)

    def _apply_score(self, lead):
        self.ensure_one()
        if self.max_score and self.current_count >= self.max_score:
            return
        lead.zakheni_lead_score = max(0, lead.zakheni_lead_score + self.score_change)
        self.current_count += 1
