from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class DigitizeController(http.Controller):

    @http.route('/zakheni/digitize/upload', type='json', auth='user', methods=['POST'])
    def upload_digitize(self, file_name, file_data, document_type_id):
        attach = request.env['ir.attachment'].create({
            'name': file_name,
            'datas': file_data,
            'res_model': 'zakheni.digitize.document',
        })
        doc = request.env['zakheni.digitize.document'].create({
            'name': file_name,
            'document_type_id': int(document_type_id),
            'attachment_id': attach.id,
        })
        doc.action_process()
        return {'id': doc.id, 'state': doc.state, 'name': doc.name}

    @http.route('/zakheni/digitize/<int:doc_id>/result', type='json', auth='user')
    def get_result(self, doc_id):
        doc = request.env['zakheni.digitize.document'].browse(doc_id)
        if not doc.exists():
            return {'error': 'Not found'}
        fields_data = [{
            'id': e.id,
            'field': e.field_id.name,
            'raw_value': e.raw_value,
            'corrected_value': e.corrected_value,
            'valid': e.is_valid,
        } for e in doc.extracted_line_ids]
        return {
            'id': doc.id,
            'name': doc.name,
            'state': doc.state,
            'ocr_text': doc.ocr_text,
            'fields': fields_data,
        }
