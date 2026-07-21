from odoo import api, fields, models, _


class TenderBidNoBid(models.Model):
    _name = 'tender.bid.no.bid'
    _description = 'Bid/No-Bid Analysis'
    _inherit = ['mail.thread']
    _rec_name = 'tender_id'

    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    company_id = fields.Many2one('res.company', related='tender_id.company_id', store=True)
    user_id = fields.Many2one('res.users', string='Analyst', default=lambda self: self.env.user, tracking=True)
    date_analysis = fields.Date(string='Analysis Date', default=fields.Date.today)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('completed', 'Completed'),
    ], string='Status', default='draft', tracking=True)

    line_ids = fields.One2many('tender.bid.no.bid.line', 'analysis_id', string='Criteria')
    total_score = fields.Float(compute='_compute_scores', string='Total Score', store=True)
    max_score = fields.Float(compute='_compute_scores', string='Maximum Score', store=True)
    score_percent = fields.Float(compute='_compute_scores', string='Score (%)', store=True)
    recommendation = fields.Selection([
        ('bid', 'Bid'),
        ('no_bid', 'No-Bid'),
        ('further_review', 'Further Review'),
    ], string='Recommendation', compute='_compute_recommendation', store=True)
    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_tender_analysis', 'UNIQUE(tender_id)', 'Only one Bid/No-Bid analysis per tender'),
    ]

    @api.depends('line_ids', 'line_ids.score', 'line_ids.weight')
    def _compute_scores(self):
        for r in self:
            total = 0.0
            max_possible = 0.0
            for line in r.line_ids:
                total += line.score * line.weight
                max_possible += 10.0 * line.weight
            r.total_score = total
            r.max_score = max_possible
            r.score_percent = (total / max_possible * 100) if max_possible else 0.0

    @api.depends('score_percent')
    def _compute_recommendation(self):
        for r in self:
            if r.score_percent >= 70:
                r.recommendation = 'bid'
            elif r.score_percent >= 40:
                r.recommendation = 'further_review'
            else:
                r.recommendation = 'no_bid'

    def open_analysis(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bid/No-Bid Analysis'),
            'res_model': 'tender.bid.no.bid',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_complete(self):
        self.state = 'completed'

    def action_draft(self):
        self.state = 'draft'


class TenderBidNoBidLine(models.Model):
    _name = 'tender.bid.no.bid.line'
    _description = 'Bid/No-Bid Criterion'
    _order = 'sequence, id'

    analysis_id = fields.Many2one('tender.bid.no.bid', string='Analysis', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    category = fields.Selection([
        ('strategic', 'Strategic Fit'),
        ('financial', 'Financial'),
        ('capacity', 'Capacity & Resources'),
        ('competitive', 'Competitive Position'),
        ('risk', 'Risk Assessment'),
        ('compliance', 'Compliance'),
    ], string='Category', required=True, default='strategic')
    name = fields.Char(string='Criterion', required=True)
    description = fields.Text(string='Description')
    weight = fields.Float(string='Weight', default=1.0, help='Importance multiplier (1-5)')
    score = fields.Float(string='Score', default=5.0, help='Score 0-10')
    notes = fields.Text(string='Notes')
