from odoo import api, fields, models


class TenderDashboard(models.TransientModel):
    _name = 'tender.dashboard'
    _description = 'Tender Dashboard'

    total_tenders = fields.Integer(compute='_compute_stats')
    total_value = fields.Monetary(compute='_compute_stats', currency_field='company_currency_id')
    won_count = fields.Integer(compute='_compute_stats')
    lost_count = fields.Integer(compute='_compute_stats')
    withdrawn_count = fields.Integer(compute='_compute_stats')
    win_rate = fields.Float(compute='_compute_stats')
    avg_value = fields.Monetary(compute='_compute_stats', currency_field='company_currency_id')
    in_progress_count = fields.Integer(compute='_compute_stats')
    won_value = fields.Monetary(compute='_compute_stats', currency_field='company_currency_id')
    pending_decision_count = fields.Integer(compute='_compute_stats')
    overdue_deadline_count = fields.Integer(compute='_compute_stats')
    company_currency_id = fields.Many2one('res.currency', compute='_compute_company_currency')

    tenders_by_stage = fields.Text(compute='_compute_chart_data')
    tenders_by_month = fields.Text(compute='_compute_chart_data')
    value_by_stage = fields.Text(compute='_compute_chart_data')

    stage_ids = fields.Many2many('tender.stage', compute='_compute_stage_list')

    def _compute_company_currency(self):
        for d in self:
            d.company_currency_id = self.env.company.currency_id

    @api.depends()
    def _compute_stats(self):
        Tender = self.env['tender.tender']
        all_tenders = Tender.search([])
        won = Tender.search([('result', '=', 'won')])
        lost = Tender.search([('result', '=', 'lost')])
        withdrawn = Tender.search([('result', '=', 'withdrawn')])
        decided_count = len(won) + len(lost) + len(withdrawn)

        for d in self:
            d.total_tenders = len(all_tenders)
            d.total_value = sum(all_tenders.mapped('tender_value'))
            d.won_count = len(won)
            d.lost_count = len(lost)
            d.withdrawn_count = len(withdrawn)
            d.win_rate = (len(won) / decided_count * 100) if decided_count else 0
            d.avg_value = sum(all_tenders.mapped('tender_value')) / len(all_tenders) if all_tenders else 0
            d.in_progress_count = len(Tender.search([('result', '=', False)]))
            d.won_value = sum(won.mapped('quoted_amount'))
            d.pending_decision_count = len(Tender.search([
                ('result', '=', False),
                ('deadline_submission', '<=', fields.Datetime.now()),
            ]))
            now = fields.Datetime.now()
            d.overdue_deadline_count = len(Tender.search([
                ('deadline_submission', '<', now),
                ('result', '=', False),
            ]))

    @api.depends()
    def _compute_chart_data(self):
        from dateutil.relativedelta import relativedelta
        now = fields.Datetime.now()
        for d in self:
            stages = self.env['tender.stage'].search([])
            stage_data = []
            for s in stages:
                count = self.env['tender.tender'].search_count([('stage_id', '=', s.id)])
                total_val = sum(self.env['tender.tender'].search([('stage_id', '=', s.id)]).mapped('tender_value'))
                if count:
                    stage_data.append({'label': s.name, 'count': count, 'value': total_val, 'sequence': s.sequence})
            stage_data.sort(key=lambda x: x['sequence'])
            d.tenders_by_stage = str(stage_data)

            months = []
            for m in range(11, -1, -1):
                start = now + relativedelta(months=-m)
                start = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = start + relativedelta(months=1)
                count = self.env['tender.tender'].search_count([
                    ('create_date', '>=', start),
                    ('create_date', '<', end),
                ])
                months.append({'month': start.strftime('%b %Y'), 'count': count})
            d.tenders_by_month = str(months)

    @api.depends()
    def _compute_stage_list(self):
        for d in self:
            d.stage_ids = self.env['tender.stage'].search([])
