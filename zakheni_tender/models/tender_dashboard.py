from odoo import api, fields, models


class TenderDashboard(models.TransientModel):
    _name = 'tender.dashboard'
    _description = 'Tender Dashboard'

    total_tenders = fields.Integer()
    total_value = fields.Monetary(currency_field='company_currency_id')
    won_count = fields.Integer()
    lost_count = fields.Integer()
    withdrawn_count = fields.Integer()
    win_rate = fields.Float()
    avg_value = fields.Monetary(currency_field='company_currency_id')
    in_progress_count = fields.Integer()
    won_value = fields.Monetary(currency_field='company_currency_id')
    pending_decision_count = fields.Integer()
    overdue_deadline_count = fields.Integer()
    company_currency_id = fields.Many2one('res.currency')

    tenders_by_stage = fields.Text()
    tenders_by_month = fields.Text()
    value_by_stage = fields.Text()

    stage_ids = fields.Many2many('tender.stage')

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        Tender = self.env['tender.tender']
        all_tenders = Tender.search([])
        won = Tender.search([('result', '=', 'won')])
        lost = Tender.search([('result', '=', 'lost')])
        withdrawn = Tender.search([('result', '=', 'withdrawn')])
        decided_count = len(won) + len(lost) + len(withdrawn)
        now = fields.Datetime.now()

        res.update({
            'company_currency_id': self.env.company.currency_id.id,
            'total_tenders': len(all_tenders),
            'total_value': sum(all_tenders.mapped('tender_value')),
            'won_count': len(won),
            'lost_count': len(lost),
            'withdrawn_count': len(withdrawn),
            'win_rate': (len(won) / decided_count * 100) if decided_count else 0,
            'avg_value': sum(all_tenders.mapped('tender_value')) / len(all_tenders) if all_tenders else 0,
            'in_progress_count': len(Tender.search([('result', '=', False)])),
            'won_value': sum(won.mapped('quoted_amount')),
            'pending_decision_count': len(Tender.search([
                ('result', '=', False),
                ('deadline_submission', '<=', now),
            ])),
            'overdue_deadline_count': len(Tender.search([
                ('deadline_submission', '<', now),
                ('result', '=', False),
            ])),
            'stage_ids': [(6, 0, self.env['tender.stage'].search([]).ids)],
            'tenders_by_stage': str(self._get_stage_chart_data()),
            'tenders_by_month': str(self._get_month_chart_data()),
        })
        return res

    @api.model
    def _get_stage_chart_data(self):
        stages = self.env['tender.stage'].search([])
        stage_data = []
        for s in stages:
            tenders = self.env['tender.tender'].search([('stage_id', '=', s.id)])
            count = len(tenders)
            total_val = sum(tenders.mapped('tender_value'))
            if count:
                stage_data.append({'label': s.name, 'count': count, 'value': total_val, 'sequence': s.sequence})
        stage_data.sort(key=lambda x: x['sequence'])
        return stage_data

    @api.model
    def _get_month_chart_data(self):
        from dateutil.relativedelta import relativedelta
        now = fields.Datetime.now()
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
        return months
