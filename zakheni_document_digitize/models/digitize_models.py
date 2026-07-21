import logging
import base64
import io
import re
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DocumentType(models.Model):
    _name = 'zakheni.document.type'
    _description = 'Document Type'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    target_model = fields.Selection([
        ('account.move', 'Vendor Bill'),
        ('res.partner', 'Contact'),
    ], string='Target Model', required=True, default='account.move')
    active = fields.Boolean(string='Active', default=True)
    extractable_field_ids = fields.One2many('zakheni.digitize.field', 'document_type_id',
                                             string='Extractable Fields')
    field_mapping_ids = fields.One2many('zakheni.digitize.field.map', 'document_type_id',
                                         string='Field Mappings')


class DigitizeField(models.Model):
    _name = 'zakheni.digitize.field'
    _description = 'Extractable Field'
    _order = 'sequence, id'

    name = fields.Char(string='Field Name', required=True, translate=True)
    field_type = fields.Selection([
        ('char', 'Text'),
        ('date', 'Date'),
        ('monetary', 'Monetary'),
        ('float', 'Float'),
        ('integer', 'Integer'),
        ('boolean', 'Boolean'),
    ], string='Field Type', default='char', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    regex_pattern = fields.Text(string='Regex Pattern',
                                 help='Regular expression to extract this field. Use capture groups for the value.')
    required = fields.Boolean(string='Required', default=False)
    odoo_field = fields.Char(string='Odoo Field',
                              help='Target field name on the target model')
    ai_hint = fields.Text(string='AI Hint',
                           help='Hint for AI-assisted extraction')
    document_type_id = fields.Many2one('zakheni.document.type', string='Document Type',
                                        ondelete='cascade', required=True)


class FieldMapping(models.Model):
    _name = 'zakheni.digitize.field.map'
    _description = 'Field Mapping'

    source_field_id = fields.Many2one('zakheni.digitize.field', string='Source Field', required=True)
    document_type_id = fields.Many2one('zakheni.document.type', string='Document Type',
                                        ondelete='cascade', required=True)
    target_field = fields.Char(string='Target Field', required=True,
                                help='Technical name of the field on the target model')
    transform = fields.Selection([
        ('direct', 'Direct Copy'),
        ('date_parse', 'Parse Date'),
        ('float_parse', 'Parse Float'),
        ('monetary_parse', 'Parse Monetary'),
        ('partner_match', 'Match Partner'),
        ('product_match', 'Match Product'),
    ], string='Transform', default='direct', required=True)

_logger = logging.getLogger(__name__)

try:
    import pdfminer
    from pdfminer.high_level import extract_text as pdf_extract_text
except ImportError:
    pdfminer = None
    pdf_extract_text = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None


class DigitizeDocument(models.Model):
    _name = 'zakheni.digitize.document'
    _description = 'Digitized Document'
    _rec_name = 'name'
    _order = 'create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Document Name', required=True, default=lambda self: _('New Document'))
    document_type_id = fields.Many2one('zakheni.document.type', string='Document Type', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Review'),
        ('reviewed', 'Reviewed'),
        ('posted', 'Posted'),
        ('error', 'Error'),
    ], string='Status', default='draft', tracking=True)
    attachment_id = fields.Many2one('ir.attachment', string='Source Document', required=True)
    file_name = fields.Char(related='attachment_id.name', string='File Name')
    file_data = fields.Binary(related='attachment_id.datas', string='File')
    ocr_text = fields.Text(string='OCR Extracted Text', readonly=True)
    error_message = fields.Text(string='Error Message', readonly=True)
    extracted_line_ids = fields.One2many('zakheni.digitize.extracted', 'document_id', string='Extracted Fields')
    target_ref = fields.Reference(
        selection=[('account.move', 'Vendor Bill'), ('res.partner', 'Contact'),
                   ('ir.attachment', 'Document')],
        string='Created Record')
    company_id = fields.Many2one('res.company', string='Company',
                                  default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='Processed By',
                               default=lambda self: self.env.user)

    def action_process(self):
        self.ensure_one()
        self.state = 'processing'
        try:
            text = self._extract_text()
            self.ocr_text = text
            self._extract_fields(text)
            self.state = 'ready'
        except Exception as e:
            _logger.exception('Digitization failed')
            self.state = 'error'
            self.error_message = str(e)

    def _extract_text(self):
        self.ensure_one()
        data = base64.b64decode(self.attachment_id.datas)
        ext = (self.file_name or '').lower()
        if ext.endswith('.pdf'):
            if pdf_extract_text is None:
                raise UserError(_('pdfminer.six is not installed'))
            text = pdf_extract_text(io.BytesIO(data))
            if text.strip():
                return text
        if pytesseract is None:
            raise UserError(_('pytesseract is not installed. Install Tesseract OCR and pytesseract.'))
        image = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(image, lang='eng')

    def _extract_fields(self, text):
        self.ensure_one()
        self.extracted_line_ids.unlink()
        fields_to_extract = self.document_type_id.extractable_field_ids
        vals_list = []
        for field_def in fields_to_extract:
            value = None
            if field_def.regex_pattern:
                match = re.search(field_def.regex_pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    value = match.group(1) if match.lastindex else match.group(0)
            else:
                lines = text.split('\n')
                for line in lines:
                    if field_def.name.lower() in line.lower():
                        value = line.split(':', 1)[-1].strip() if ':' in line else line
                        break
            if value is not None:
                vals_list.append({
                    'document_id': self.id,
                    'field_id': field_def.id,
                    'raw_value': str(value).strip(),
                    'field_type': field_def.field_type,
                })
        if vals_list:
            self.env['zakheni.digitize.extracted'].create(vals_list)

    def action_validate(self):
        self.ensure_one()
        self.state = 'reviewed'

    def action_create_record(self):
        self.ensure_one()
        target = self.document_type_id.target_model
        vals = self._prepare_target_vals()
        record = self.env[target].create(vals)
        if 'account.move' in target:
            if self.attachment_id:
                record.message_post(attachment_ids=[self.attachment_id.id])
        self.target_ref = '%s,%d' % (target, record.id)
        self.state = 'posted'
        return {
            'type': 'ir.actions.act_window',
            'res_model': target,
            'res_id': record.id,
            'view_mode': 'form',
        }

    def _prepare_target_vals(self):
        self.ensure_one()
        vals = {}
        for mapping in self.document_type_id.field_mapping_ids:
            extracted = self.extracted_line_ids.filtered(
                lambda e, m=mapping: e.field_id == m.source_field_id)
            if extracted:
                vals[mapping.target_field] = self._transform_value(
                    extracted[0].raw_value, mapping.transform)
        return vals

    def _transform_value(self, raw, transform):
        if transform == 'direct':
            return raw
        elif transform == 'date_parse':
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y'):
                try:
                    return datetime.strptime(raw, fmt).date()
                except ValueError:
                    continue
            return raw
        elif transform == 'float_parse':
            cleaned = re.sub(r'[^\d.,-]', '', raw)
            cleaned = cleaned.replace(',', '')
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        elif transform == 'monetary_parse':
            cleaned = re.sub(r'[^\d.,-]', '', raw)
            if ',' in cleaned and '.' in cleaned:
                cleaned = cleaned.replace(',', '')
            elif ',' in cleaned:
                cleaned = cleaned.replace(',', '.')
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        elif transform == 'partner_match':
            return self.env['res.partner'].search([('name', 'ilike', raw)], limit=1).id or False
        elif transform == 'product_match':
            return self.env['product.product'].search([('name', 'ilike', raw)], limit=1).id or False
        return raw

    def action_retry(self):
        self.ensure_one()
        self.error_message = False
        self.state = 'draft'
        self.action_process()


class ExtractedField(models.Model):
    _name = 'zakheni.digitize.extracted'
    _description = 'Extracted Field Value'
    _rec_name = 'field_id'

    document_id = fields.Many2one('zakheni.digitize.document', string='Document', required=True)
    field_id = fields.Many2one('zakheni.digitize.field', string='Field', required=True)
    field_type = fields.Selection(related='field_id.field_type', string='Type', store=True)
    raw_value = fields.Text(string='Extracted Value')
    corrected_value = fields.Text(string='Corrected Value')
    confidence = fields.Float(string='Confidence', default=0.0)
    is_valid = fields.Boolean(string='Valid', default=True)

    def action_accept(self):
        self.is_valid = True

    def action_reject(self):
        self.is_valid = False


class ResPartner(models.Model):
    _inherit = 'res.partner'

    digitize_document_ids = fields.One2many('zakheni.digitize.document',
                                             compute='_compute_digitize_documents')

    def _compute_digitize_documents(self):
        for partner in self:
            partner.digitize_document_ids = self.env['zakheni.digitize.document'].search([
                ('target_ref', '=', 'res.partner,%d' % partner.id)
            ])


class AccountMove(models.Model):
    _inherit = 'account.move'

    digitize_document_ids = fields.One2many('zakheni.digitize.document',
                                             compute='_compute_digitize_documents')

    def _compute_digitize_documents(self):
        for move in self:
            move.digitize_document_ids = self.env['zakheni.digitize.document'].search([
                ('target_ref', '=', 'account.move,%d' % move.id)
            ])
