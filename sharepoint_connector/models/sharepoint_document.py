import logging

from odoo import fields, models, _

_logger = logging.getLogger(__name__)


class SharePointDocumentLibrary(models.Model):
    _name = 'sharepoint.document.library'
    _description = 'SharePoint Document Library Sync'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    site_id = fields.Many2one('sharepoint.site', string='SharePoint Site', required=True)
    library_name = fields.Char(string='Document Library Name', required=True)
    folder_path = fields.Char(string='Folder Path')
    odoo_model = fields.Selection([
        ('ir.attachment', 'Attachments'),
        ('dms.file', 'DMS Files'),
    ], string='Odoo Model', default='ir.attachment', required=True)
    sync_direction = fields.Selection([
        ('bidirectional', 'Bidirectional'),
        ('odoo_to_sharepoint', 'Odoo → SharePoint'),
        ('sharepoint_to_odoo', 'SharePoint → Odoo'),
    ], string='Sync Direction', default='bidirectional', required=True)
    active = fields.Boolean(default=True)

    def action_sync_now(self):
        for record in self:
            record._sync_library()
        return {'type': 'ir.actions.act_window_message', 'title': _('Sync Complete'), 'message': _('Document library sync completed.')}

    def _get_client(self):
        return self.site_id._get_client()

    def _sync_library(self):
        client = self._get_client()
        library = client.web.lists.get_by_title(self.library_name)
        client.load(library)
        client.execute_query()
        items = library.items
        client.load(items)
        client.execute_query()

    def _run_scheduled_sync(self):
        libraries = self.search([('active', '=', True)])
        for library in libraries:
            try:
                library._sync_library()
            except Exception as e:
                _logger.error('Scheduled sync failed for library %s: %s', library.name, e)


class SharePointDocumentSync(models.Model):
    _name = 'sharepoint.document.sync'
    _description = 'SharePoint Document Sync History'
    _rec_name = 'file_name'

    file_name = fields.Char(string='File Name')
    sharepoint_path = fields.Char(string='SharePoint Path')
    attachment_id = fields.Many2one('ir.attachment', string='Odoo Attachment')
    dms_file_id = fields.Many2one('dms.file', string='DMS File')
    sync_direction = fields.Selection([
        ('upload', 'Uploaded to SharePoint'),
        ('download', 'Downloaded from SharePoint'),
    ], string='Direction')
    sync_date = fields.Datetime(string='Sync Date', default=fields.Datetime.now)
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
    ], string='Status', default='success')
    error_message = fields.Text(string='Error Message')
    library_id = fields.Many2one('sharepoint.document.library', string='Document Library')
