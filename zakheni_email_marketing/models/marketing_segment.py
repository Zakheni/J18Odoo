from odoo import api, fields, models, _
from odoo.osv import expression


class MarketingSegment(models.Model):
    _name = 'marketing.segment'
    _description = 'Marketing Segment'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char('Segment Name', required=True)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')
    color = fields.Integer('Color Index')

    model_id = fields.Many2one(
        'ir.model', string='Target Model',
        required=True, ondelete='cascade',
        default=lambda self: self.env.ref('mass_mailing.model_mailing_contact').id,
        domain=[('is_mailing_enabled', '=', True)])
    model_name = fields.Char(
        string='Model Name',
        related='model_id.model', readonly=True, store=True)

    domain = fields.Text(
        'Segment Domain',
        required=True, default='[]',
        help='Domain expression defining this segment.')
    domain_description = fields.Char(
        'Description', compute='_compute_domain_description')

    is_dynamic = fields.Boolean(
        'Dynamic Segment',
        default=True,
        help='Automatically updated segment based on domain.')
    contact_count = fields.Integer(
        'Contact Count', compute='_compute_contact_count')

    list_ids = fields.Many2many(
        'mailing.list', string='Mailing Lists',
        help='Mailing lists associated with this segment.')
    campaign_ids = fields.Many2many(
        'marketing.campaign', string='Campaigns')

    condition_type = fields.Selection([
        ('demographic', 'Demographic'),
        ('behavioral', 'Behavioral'),
        ('engagement', 'Engagement Level'),
        ('purchase', 'Purchase History'),
        ('email', 'Email Activity'),
        ('custom', 'Custom Domain'),
    ], string='Condition Type', default='custom')

    min_engagement_score = fields.Float('Min Engagement Score')
    max_engagement_score = fields.Float('Max Engagement Score')
    min_lead_score = fields.Integer('Min Lead Score')
    max_lead_score = fields.Integer('Max Lead Score')
    min_total_opens = fields.Integer('Min Total Opens')
    min_total_clicks = fields.Integer('Min Total Clicks')
    last_open_within_days = fields.Integer('Last Open Within (Days)')
    last_click_within_days = fields.Integer('Last Click Within (Days)')

    category = fields.Selection([
        ('new', 'New Subscribers'),
        ('active', 'Active & Engaged'),
        ('dormant', 'Dormant / At Risk'),
        ('churned', 'Churned / Lost'),
        ('high_value', 'High Value'),
        ('converted', 'Converted Customers'),
        ('custom', 'Custom Segment'),
    ], string='Segment Category', default='custom')

    @api.depends('domain')
    def _compute_domain_description(self):
        for segment in self:
            if segment.domain and segment.domain != '[]':
                segment.domain_description = _('Custom filter applied')
            else:
                segment.domain_description = _('No filter')

    @api.depends('domain', 'is_dynamic', 'model_name', 'condition_type',
                 'min_engagement_score', 'max_engagement_score',
                 'min_lead_score', 'max_lead_score',
                 'min_total_opens', 'min_total_clicks',
                 'last_open_within_days', 'last_click_within_days')
    def _compute_contact_count(self):
        for segment in self:
            try:
                domain = segment._build_domain()
                model = segment.model_name or 'mailing.contact'
                segment.contact_count = self.env[model].search_count(domain)
            except Exception:
                segment.contact_count = 0

    def _build_domain(self):
        self.ensure_one()
        domain_parts = []
        if self.condition_type == 'engagement':
            if self.min_engagement_score:
                domain_parts.append(('engagement_score', '>=', self.min_engagement_score))
            if self.max_engagement_score:
                domain_parts.append(('engagement_score', '<=', self.max_engagement_score))
        elif self.condition_type == 'behavioral':
            if self.min_lead_score:
                domain_parts.append(('lead_score', '>=', self.min_lead_score))
            if self.max_lead_score:
                domain_parts.append(('lead_score', '<=', self.max_lead_score))
            if self.min_total_opens:
                domain_parts.append(('total_opens', '>=', self.min_total_opens))
            if self.min_total_clicks:
                domain_parts.append(('total_clicks', '>=', self.min_total_clicks))
            if self.last_open_within_days:
                from datetime import datetime, timedelta
                cutoff = datetime.now() - timedelta(days=self.last_open_within_days)
                domain_parts.append(('last_open_date', '>=', cutoff))
            if self.last_click_within_days:
                from datetime import datetime, timedelta
                cutoff = datetime.now() - timedelta(days=self.last_click_within_days)
                domain_parts.append(('last_click_date', '>=', cutoff))
        elif self.condition_type == 'custom' and self.domain:
            try:
                domain_parts.append(eval(self.domain))
            except Exception:
                pass
        if not domain_parts:
            domain_parts = [[]]
        return expression.AND(domain_parts)

    def _get_contacts(self):
        self.ensure_one()
        domain = self._build_domain()
        model = self.model_name or 'mailing.contact'
        if model == 'mailing.contact':
            return self.env[model].search(domain)
        return self.env[model].search(domain)

    def action_view_contacts(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Segment Contacts'),
            'res_model': self.model_name or 'mailing.contact',
            'domain': self._build_domain(),
            'view_mode': 'tree,form',
        }
