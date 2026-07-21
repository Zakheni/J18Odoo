from odoo import api, fields, models


class MarketingReport(models.Model):
    _name = 'marketing.report'
    _description = 'Marketing Report'
    _auto = False
    _rec_name = 'campaign_id'
    _order = 'campaign_id'

    campaign_id = fields.Many2one('marketing.campaign', string='Campaign', readonly=True)
    mailing_id = fields.Many2one('mailing.mailing', string='Mailing', readonly=True)
    date = fields.Date('Date', readonly=True)
    sent_count = fields.Integer('Sent', readonly=True)
    opened_count = fields.Integer('Opened', readonly=True)
    clicked_count = fields.Integer('Clicked', readonly=True)
    bounced_count = fields.Integer('Bounced', readonly=True)
    replied_count = fields.Integer('Replied', readonly=True)
    conversion_count = fields.Integer('Conversions', readonly=True)

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW marketing_report AS (
                SELECT
                    MIN(mt.id) AS id,
                    mm.zakheni_campaign_id AS campaign_id,
                    mt.mass_mailing_id AS mailing_id,
                    mt.sent_datetime::date AS date,
                    COUNT(*) AS sent_count,
                    COUNT(CASE WHEN mt.trace_status IN ('open', 'reply') THEN 1 END) AS opened_count,
                    COUNT(CASE WHEN mt.links_click_datetime IS NOT NULL THEN 1 END) AS clicked_count,
                    COUNT(CASE WHEN mt.trace_status = 'bounce' THEN 1 END) AS bounced_count,
                    COUNT(CASE WHEN mt.trace_status = 'reply' THEN 1 END) AS replied_count,
                    COUNT(CASE WHEN mt.zakheni_conversion_date IS NOT NULL THEN 1 END) AS conversion_count
                FROM mailing_trace mt
                JOIN mailing_mailing mm ON mt.mass_mailing_id = mm.id
                GROUP BY mm.zakheni_campaign_id, mt.mass_mailing_id, mt.sent_datetime::date
            )
        """)
