from odoo import api, fields, models, _


class MarketingROI(models.Model):
    _name = 'marketing.roi'
    _description = 'Marketing ROI Analysis'
    _rec_name = 'name'
    _order = 'create_date DESC'

    name = fields.Char('Analysis Name', required=True)
    campaign_id = fields.Many2one(
        'marketing.campaign', string='Campaign',
        ondelete='cascade')
    mailing_id = fields.Many2one(
        'mailing.mailing', string='Mailing',
        ondelete='set null')

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
    ], string='Status', default='draft')

    total_sent = fields.Integer('Total Sent', readonly=True)
    total_delivered = fields.Integer('Total Delivered', readonly=True)
    total_opened = fields.Integer('Total Opened', readonly=True)
    total_clicked = fields.Integer('Total Clicked', readonly=True)
    total_converted = fields.Integer('Total Converted', readonly=True)
    total_bounced = fields.Integer('Total Bounced', readonly=True)

    cost_per_email = fields.Float('Cost per Email', default=0.01)
    total_cost = fields.Monetary(
        'Total Cost', compute='_compute_costs',
        currency_field='currency_id')
    campaign_cost = fields.Monetary(
        'Campaign Cost', currency_field='currency_id',
        help='Additional campaign costs (design, tools, etc.)')
    total_investment = fields.Monetary(
        'Total Investment', compute='_compute_costs',
        currency_field='currency_id')

    total_revenue = fields.Monetary(
        'Total Revenue', currency_field='currency_id')
    attributed_revenue = fields.Monetary(
        'Attributed Revenue', currency_field='currency_id',
        help='Revenue attributed to this campaign.')

    roi_amount = fields.Monetary(
        'ROI Amount', compute='_compute_roi',
        currency_field='currency_id')
    roi_percentage = fields.Float(
        'ROI %', compute='_compute_roi')
    cost_per_lead = fields.Monetary(
        'Cost per Lead', compute='_compute_cpl',
        currency_field='currency_id')
    cost_per_acquisition = fields.Monetary(
        'Cost per Acquisition', compute='_compute_cpa',
        currency_field='currency_id')
    conversion_rate = fields.Float(
        'Conversion Rate', compute='_compute_rates')
    open_rate = fields.Float('Open Rate', compute='_compute_rates')
    click_rate = fields.Float('Click Rate', compute='_compute_rates')
    click_to_open_rate = fields.Float(
        'Click-to-Open Rate', compute='_compute_rates')

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id)
    notes = fields.Text('Notes')

    @api.depends('total_sent', 'cost_per_email', 'campaign_cost')
    def _compute_costs(self):
        for roi in self:
            roi.total_cost = roi.total_sent * roi.cost_per_email
            roi.total_investment = roi.total_cost + roi.campaign_cost

    @api.depends('attributed_revenue', 'total_investment')
    def _compute_roi(self):
        for roi in self:
            if roi.total_investment:
                roi.roi_amount = roi.attributed_revenue - roi.total_investment
                roi.roi_percentage = round(
                    (roi.attributed_revenue - roi.total_investment) /
                    roi.total_investment * 100, 2)
            else:
                roi.roi_amount = 0.0
                roi.roi_percentage = 0.0

    @api.depends('total_cost', 'total_converted', 'total_delivered')
    def _compute_cpl(self):
        for roi in self:
            leads = max(roi.total_converted, 1)
            roi.cost_per_lead = roi.total_cost / leads

    @api.depends('total_cost', 'total_converted')
    def _compute_cpa(self):
        for roi in self:
            acquisitions = max(roi.total_converted, 1)
            roi.cost_per_acquisition = roi.total_cost / acquisitions

    @api.depends('total_delivered', 'total_opened',
                 'total_clicked', 'total_converted')
    def _compute_rates(self):
        for roi in self:
            delivered = max(roi.total_delivered, 1)
            opened = max(roi.total_opened, 1)
            roi.open_rate = round(100.0 * roi.total_opened / delivered, 2)
            roi.click_rate = round(100.0 * roi.total_clicked / delivered, 2)
            roi.click_to_open_rate = round(100.0 * roi.total_clicked / opened, 2)
            roi.conversion_rate = round(100.0 * roi.total_converted / delivered, 2)

    def action_calculate(self):
        self.ensure_one()
        mailing = self.mailing_id
        if mailing:
            self.total_sent = mailing.sent
            self.total_delivered = mailing.delivered
            self.total_opened = mailing.opened
            self.total_clicked = mailing.clicked
            self.total_bounced = mailing.bounced
            self.total_converted = mailing.conversion_count
        elif self.campaign_id:
            mailings = self.campaign_id.mailing_ids
            self.total_sent = sum(mailings.mapped('sent'))
            self.total_delivered = sum(mailings.mapped('delivered'))
            self.total_opened = sum(mailings.mapped('opened'))
            self.total_clicked = sum(mailings.mapped('clicked'))
            self.total_bounced = sum(mailings.mapped('bounced'))
            self.total_converted = sum(mailings.mapped('conversion_count'))
        self.state = 'calculated'
