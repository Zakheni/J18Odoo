from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class MarketingCampaign(models.Model):
    _name = 'marketing.campaign'
    _description = 'Marketing Campaign'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'create_date DESC'

    name = fields.Char('Campaign Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True,
       group_expand=True)
    campaign_type = fields.Selection([
        ('email', 'Email Campaign'),
        ('sms', 'SMS Campaign'),
        ('multichannel', 'Multi-Channel Campaign'),
        ('reengagement', 'Re-engagement Campaign'),
        ('automated', 'Automated Trigger Campaign'),
    ], string='Campaign Type', default='email', required=True)
    color = fields.Integer('Color Index')
    user_id = fields.Many2one(
        'res.users', string='Campaign Manager',
        default=lambda self: self.env.user, tracking=True)
    team_id = fields.Many2one(
        'crm.team', string='Sales Team')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.company)

    start_date = fields.Datetime('Start Date', tracking=True)
    end_date = fields.Datetime('End Date', tracking=True)
    budget = fields.Monetary('Budget', currency_field='currency_id', tracking=True)
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)

    description = fields.Html('Description')
    goal = fields.Text('Campaign Goal')

    step_ids = fields.One2many(
        'marketing.campaign.step', 'campaign_id',
        string='Campaign Steps', copy=True)
    step_count = fields.Integer('Steps', compute='_compute_step_count')

    mailing_ids = fields.One2many(
        'mailing.mailing', 'zakheni_campaign_id',
        string='Mailings', context={'active_test': False})
    mailing_count = fields.Integer('Mailings', compute='_compute_mailing_count')
    sent_count = fields.Integer('Sent', compute='_compute_campaign_stats')
    opened_count = fields.Integer('Opened', compute='_compute_campaign_stats')
    clicked_count = fields.Integer('Clicked', compute='_compute_campaign_stats')
    bounced_count = fields.Integer('Bounced', compute='_compute_campaign_stats')
    replied_count = fields.Integer('Replied', compute='_compute_campaign_stats')
    open_rate = fields.Float('Open Rate', compute='_compute_campaign_stats')
    click_rate = fields.Float('Click Rate', compute='_compute_campaign_stats')
    conversion_rate = fields.Float('Conversion Rate', compute='_compute_campaign_stats')

    segment_ids = fields.Many2many(
        'marketing.segment', string='Target Segments')
    target_list_ids = fields.Many2many(
        'mailing.list', string='Target Mailing Lists')
    total_recipients = fields.Integer('Total Recipients', compute='_compute_total_recipients')

    utm_campaign_id = fields.Many2one(
        'utm.campaign', string='UTM Campaign',
        ondelete='set null', copy=False)

    landing_page_ids = fields.One2many(
        'marketing.landing.page', 'campaign_id', string='Landing Pages')

    reengagement_config_id = fields.Many2one(
        'marketing.reengagement', string='Re-engagement Config')

    lead_score_config_ids = fields.One2many(
        'marketing.lead.score', 'campaign_id', string='Lead Scoring Rules')

    roi_analysis_ids = fields.One2many(
        'marketing.roi', 'campaign_id', string='ROI Analysis')

    @api.depends('step_ids')
    def _compute_step_count(self):
        for campaign in self:
            campaign.step_count = len(campaign.step_ids)

    @api.depends('mailing_ids')
    def _compute_mailing_count(self):
        for campaign in self:
            campaign.mailing_count = len(campaign.mailing_ids)

    @api.depends('mailing_ids.sent', 'mailing_ids.opened',
                 'mailing_ids.clicked', 'mailing_ids.bounced',
                 'mailing_ids.replied', 'mailing_ids.total')
    def _compute_campaign_stats(self):
        for campaign in self:
            mailings = campaign.mailing_ids
            campaign.sent_count = sum(mailings.mapped('sent'))
            campaign.opened_count = sum(mailings.mapped('opened'))
            campaign.clicked_count = sum(mailings.mapped('clicked'))
            campaign.bounced_count = sum(mailings.mapped('bounced'))
            campaign.replied_count = sum(mailings.mapped('replied'))
            total_delivered = campaign.sent_count or 1
            campaign.open_rate = round(100.0 * campaign.opened_count / total_delivered, 2)
            campaign.click_rate = round(100.0 * campaign.clicked_count / total_delivered, 2)
            campaign.conversion_rate = round(
                100.0 * campaign.clicked_count / total_delivered, 2) if total_delivered else 0.0

    @api.depends('segment_ids', 'target_list_ids')
    def _compute_total_recipients(self):
        for campaign in self:
            total = 0
            for segment in campaign.segment_ids:
                total += segment.contact_count
            for lst in campaign.target_list_ids:
                total += lst.contact_count
            campaign.total_recipients = total

    def action_start(self):
        self.write({'state': 'running', 'start_date': fields.Datetime.now()})
        for step in self.step_ids.filtered(lambda s: s.trigger_type == 'immediate'):
            step._execute_step()

    def action_pause(self):
        self.write({'state': 'paused'})

    def action_resume(self):
        self.write({'state': 'running'})

    def action_complete(self):
        self.write({'state': 'completed', 'end_date': fields.Datetime.now()})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_duplicate_campaign(self):
        self.ensure_one()
        new_campaign = self.copy({
            'name': _('%s (copy)') % self.name,
            'state': 'draft',
        })
        for step in self.step_ids:
            step.copy({'campaign_id': new_campaign.id})
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'marketing.campaign',
            'res_id': new_campaign.id,
        }

    def _cron_process_automated_campaigns(self):
        campaigns = self.search([
            ('state', '=', 'running'),
            ('campaign_type', '=', 'automated'),
        ])
        for campaign in campaigns:
            for step in campaign.step_ids.filtered(lambda s: s.trigger_type == 'scheduled'):
                step._execute_step()
