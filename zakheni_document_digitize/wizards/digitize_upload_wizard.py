from odoo import api, fields, models, _


class DigitizeUploadWizard(models.TransientModel):
    _name = 'zakheni.digitize.upload.wizard'
    _description = 'Upload Document for Digitization'

    document_type_id = fields.Many2one('zakheni.document.type', string='Document Type', required=True)
    file_name = fields.Char(string='File Name')
    file_data = fields.Binary(string='Document File', required=True)
    company_id = fields.Many2one('res.company', string='Company',
                                  default=lambda self: self.env.company)

    def action_upload_and_process(self):
        self.ensure_one()
        attach = self.env['ir.attachment'].create({
            'name': self.file_name or 'scanned_document.pdf',
            'datas': self.file_data,
            'res_model': 'zakheni.digitize.document',
        })
        doc = self.env['zakheni.digitize.document'].create({
            'name': self.file_name or 'Scanned Document',
            'document_type_id': self.document_type_id.id,
            'attachment_id': attach.id,
            'company_id': self.company_id.id,
        })
        doc.action_process()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'zakheni.digitize.document',
            'res_id': doc.id,
            'view_mode': 'form',
            'target': 'current',
        }
