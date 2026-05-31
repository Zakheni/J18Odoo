from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    google_api_key = fields.Char(
        string='Google Custom Search API Key',
        config_parameter='zakheni_partner_enrich.google_api_key',
        help='API key from Google Cloud Console (requires Custom Search API enabled).',
    )
    google_cx = fields.Char(
        string='Google Search Engine ID (cx)',
        config_parameter='zakheni_partner_enrich.google_cx',
        help='Search Engine ID from https://programmablesearchengine.google.com/',
    )
