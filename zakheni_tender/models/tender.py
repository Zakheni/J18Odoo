from odoo import api, fields, models, _


class Tender(models.Model):
    _name = 'tender.tender'
    _description = 'Tender'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'deadline_submission, id'
    # Core
    name = fields.Char(string='Tender Name', required=True, tracking=True)
    tender_number = fields.Char(string='Tender Reference', help='Reference number from the issuer.')
    issuer_id = fields.Many2one('res.partner', string='Issuer', tracking=True)
    description = fields.Html(string='Scope of Work')

    # Stage
    stage_id = fields.Many2one(
        'tender.stage',
        string='Stage',
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id(),
        index=True,
        tracking=True,
    )

    # Dates
    deadline_submission = fields.Datetime(string='Submission Deadline', tracking=True)
    deadline_validity = fields.Date(string='Validity Period End')
    date_site_visit = fields.Datetime(string='Site Visit')
    date_briefing = fields.Datetime(string='Briefing Session')
    preparation_deadline = fields.Date(string='Preparation Deadline')
    date_published = fields.Date(string='Publication Date')
    date_submitted = fields.Datetime(string='Date Submitted', tracking=True)
    date_award = fields.Date(string='Award Date', tracking=True)

    # Financial
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    tender_value = fields.Monetary(string='Estimated Tender Value', currency_field='currency_id')
    quoted_amount = fields.Monetary(string='Our Quoted Amount', currency_field='currency_id', tracking=True)
    bid_bond_amount = fields.Monetary(string='Bid Bond Amount', currency_field='currency_id')
    bid_bond_expiry = fields.Date(string='Bid Bond Expiry')
    bid_bond_bank = fields.Char(string='Bid Bond Bank')
    estimated_bid_cost = fields.Monetary(string='Estimated Bid Cost', currency_field='currency_id', help='Internal cost to prepare and submit this bid.')

    # Evaluation
    probability = fields.Float(string='Win Probability (%)', aggregator='avg')
    competitive_bidding = fields.Boolean(string='Competitive Bidding')

    # Result
    result = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('withdrawn', 'Withdrawn'),
        ('cancelled', 'Cancelled'),
    ], string='Result', tracking=True)
    result_date = fields.Date(string='Result Date')
    lost_reason = fields.Text(string='Reason Lost')
    competitor_ids = fields.Many2many('res.partner', string='Competitors')

    # Team
    user_id = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user, tracking=True)
    team_ids = fields.Many2many('res.users', 'tender_team_rel', 'tender_id', 'user_id', string='Team Members')

    document_ids = fields.One2many('tender.document', 'tender_id', string='Documents')
    document_count = fields.Integer(compute='_compute_document_count', string='Document Count')
    resource_ids = fields.One2many('tender.document.resource', 'tender_id', string='Resources')

    # Company & Active
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')

    # --- Computes ---

    @api.depends('name', 'tender_number')
    def _compute_display_name(self):
        for t in self:
            parts = [p for p in (t.tender_number, t.name) if p]
            t.display_name = ' — '.join(parts) if len(parts) == 2 else (parts[0] if parts else '')

    def name_get(self):
        result = []
        for t in self:
            parts = [p for p in (t.tender_number, t.name) if p]
            name = ' — '.join(parts) if len(parts) == 2 else (parts[0] if parts else '')
            result.append((t.id, name))
        return result

    @api.depends('document_ids')
    def _compute_document_count(self):
        for t in self:
            t.document_count = len(t.document_ids)

    @api.model
    def _default_stage_id(self):
        return self.env['tender.stage'].search([], order='sequence', limit=1).id

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['tender.stage'].search([])

    # --- Actions ---

    def action_view_documents(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Documents'),
            'res_model': 'tender.document',
            'view_mode': 'list,form',
            'domain': [('tender_id', '=', self.id)],
            'context': {'default_tender_id': self.id},
        }

    def action_won(self):
        for t in self:
            t.result = 'won'
            t.result_date = fields.Date.today()
            won_stage = self.env['tender.stage'].search([('is_won', '=', True)], limit=1)
            if won_stage:
                t.stage_id = won_stage

    def action_lost(self):
        for t in self:
            t.result = 'lost'
            t.result_date = fields.Date.today()
            lost_stage = self.env['tender.stage'].search([('is_lost', '=', True)], limit=1)
            if lost_stage:
                t.stage_id = lost_stage

    def action_withdraw(self):
        for t in self:
            t.result = 'withdrawn'
            t.result_date = fields.Date.today()
