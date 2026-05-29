import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class SharePointSite(models.Model):
    _name = 'sharepoint.site'
    _description = 'SharePoint Site'
    _rec_name = 'name'

    name = fields.Char(string='Site Name', required=True)
    site_url = fields.Char(string='Site URL', required=True)
    config_id = fields.Many2one('sharepoint.config', string='Configuration', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', related='config_id.company_id', store=True)
    document_library_count = fields.Integer(compute='_compute_counts')
    list_count = fields.Integer(compute='_compute_counts')

    def _compute_counts(self):
        DocLibrary = self.env['sharepoint.document.library']
        SPList = self.env['sharepoint.list']
        for record in self:
            record.document_library_count = DocLibrary.search_count([('site_id', '=', record.id)])
            record.list_count = SPList.search_count([('site_id', '=', record.id)])

    def _get_client(self):
        self.ensure_one()
        return self.config_id._get_client(self.site_url)
