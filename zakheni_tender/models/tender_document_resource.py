from odoo import fields, models


class TenderDocumentResource(models.Model):
    _name = 'tender.document.resource'
    _description = 'Document Resource'
    _order = 'sequence, name'

    name = fields.Char(string='Name', required=True)
    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    document_ids = fields.One2many('tender.document', 'resource_id', string='Documents')
