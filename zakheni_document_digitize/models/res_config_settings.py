from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ocr_engine = fields.Selection([
        ('tesseract', 'Tesseract OCR (Local)'),
        ('google_vision', 'Google Cloud Vision API'),
        ('azure_doc_intel', 'Azure AI Document Intelligence'),
    ], string='OCR Engine', default='tesseract',
        config_parameter='zakheni_digitize.ocr_engine')

    google_vision_api_key = fields.Char(string='Google Vision API Key',
        config_parameter='zakheni_digitize.google_vision_api_key')

    azure_endpoint = fields.Char(string='Azure Endpoint',
        config_parameter='zakheni_digitize.azure_endpoint')
    azure_api_key = fields.Char(string='Azure API Key',
        config_parameter='zakheni_digitize.azure_api_key')

    tesseract_lang = fields.Char(string='Tesseract Language',
        default='eng',
        config_parameter='zakheni_digitize.tesseract_lang')

    tesseract_path = fields.Char(string='Tesseract Executable Path',
        default='C:\\Program Files\\Tesseract-OCR\\tesseract.exe',
        config_parameter='zakheni_digitize.tesseract_path')
