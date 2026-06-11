from odoo import api, fields, models


class TenderAnalysis(models.Model):
    _name = 'tender.analysis'
    _description = 'Tender Analysis'
    _auto = False
    _order = 'date_desc'

    date = fields.Date('Date')
    tender_id = fields.Many2one('tender.tender', 'Tender')
    user_id = fields.Many2one('res.users', 'Responsible')
    stage_id = fields.Many2one('tender.stage', 'Stage')
    issuer_id = fields.Many2one('res.partner', 'Issuer')
    company_id = fields.Many2one('res.company', 'Company')
    result = fields.Selection([
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('withdrawn', 'Withdrawn'),
        ('cancelled', 'Cancelled'),
    ], 'Result')
    date_desc = fields.Datetime('Date Description')

    tender_value = fields.Monetary('Tender Value', currency_field='currency_id')
    quoted_amount = fields.Monetary('Quoted Amount', currency_field='currency_id')
    probability = fields.Float('Win Probability')
    duration_days = fields.Integer('Duration (Days)')
    is_won = fields.Boolean('Is Won')
    is_lost = fields.Boolean('Is Lost')
    currency_id = fields.Many2one('res.currency', 'Currency')

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW tender_analysis AS (
                SELECT
                    t.id AS id,
                    t.id AS tender_id,
                    t.create_date AS date,
                    t.create_date AS date_desc,
                    t.user_id,
                    t.stage_id,
                    t.issuer_id,
                    t.company_id,
                    t.result,
                    t.tender_value,
                    t.quoted_amount,
                    t.probability,
                    t.currency_id,
                    CASE WHEN t.result = 'won' THEN TRUE ELSE FALSE END AS is_won,
                    CASE WHEN t.result = 'lost' THEN TRUE ELSE FALSE END AS is_lost,
                    COALESCE(
                        EXTRACT(DAY FROM (t.date_award::timestamp - t.date_published::timestamp)),
                        0
                    )::integer AS duration_days
                FROM tender_tender t
            )
        """)
