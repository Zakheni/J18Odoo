from odoo import api, fields, models


class TenderDocument(models.Model):
    _name = 'tender.document'
    _description = 'Tender Document'
    _order = 'name'
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=False)
    name = fields.Char(string='File Name', required=True)
    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    resource_id = fields.Many2one('tender.document.resource', string='Resource', ondelete='cascade')
    datas = fields.Binary(string='File', attachment=True)
    file_size = fields.Integer(string='File Size (bytes)')
    uploaded_by = fields.Many2one('res.users', string='Uploaded by', default=lambda self: self.env.user)
    uploaded_date = fields.Datetime(string='Upload Date', default=fields.Datetime.now)

    @api.depends('name')
    def _compute_display_name(self):
        for d in self:
            d.display_name = d.name
