from odoo import api, fields, models, _


class MarketingLandingPage(models.Model):
    _name = 'marketing.landing.page'
    _description = 'Marketing Landing Page'
    _inherit = ['mail.thread']
    _rec_name = 'name'
    _order = 'create_date DESC'

    name = fields.Char('Page Name', required=True, tracking=True)
    active = fields.Boolean('Active', default=True)

    campaign_id = fields.Many2one(
        'marketing.campaign', string='Campaign',
        ondelete='cascade')
    mailing_id = fields.Many2one(
        'mailing.mailing', string='Mailing',
        ondelete='set null')

    url = fields.Char('Page URL', required=True)
    body_html = fields.Html(
        'Page Content',
        sanitize=False,
        sanitize_attributes=False)
    body_arch = fields.Html(
        'Page Architecture',
        sanitize=False,
        sanitize_attributes=False)

    page_type = fields.Selection([
        ('subscribe', 'Subscription Form'),
        ('unsubscribe', 'Unsubscribe'),
        ('lead_capture', 'Lead Capture'),
        ('promotion', 'Promotional'),
        ('event', 'Event Registration'),
        ('thank_you', 'Thank You / Confirmation'),
        ('custom', 'Custom Page'),
    ], string='Page Type', default='lead_capture', required=True)

    template_id = fields.Many2one(
        'marketing.landing.page', string='Template',
        domain="[('page_type', '=', page_type)]")

    lead_team_id = fields.Many2one(
        'crm.team', string='Lead Team')
    mailing_list_id = fields.Many2one(
        'mailing.list', string='Subscribe to List')

    total_views = fields.Integer('Total Views', default=0)
    total_submissions = fields.Integer('Total Submissions', default=0)
    conversion_rate = fields.Float(
        'Conversion Rate',
        compute='_compute_conversion_rate')

    @api.depends('total_views', 'total_submissions')
    def _compute_conversion_rate(self):
        for page in self:
            if page.total_views:
                page.conversion_rate = round(
                    100.0 * page.total_submissions / page.total_views, 2)
            else:
                page.conversion_rate = 0.0

    def action_view_page(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.url,
            'target': 'new',
        }

    def register_view(self):
        self.ensure_one()
        self.total_views += 1

    def register_submission(self):
        self.ensure_one()
        self.total_submissions += 1
