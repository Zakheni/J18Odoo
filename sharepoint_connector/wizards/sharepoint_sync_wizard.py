import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SharePointSyncWizard(models.TransientModel):
    _name = 'sharepoint.sync.wizard'
    _description = 'SharePoint Sync Wizard'

    library_id = fields.Many2one('sharepoint.document.library', string='Document Library')
    list_id = fields.Many2one('sharepoint.list', string='SharePoint List')
    sync_type = fields.Selection([
        ('document', 'Document Library'),
        ('list', 'List'),
    ], string='Sync Type', required=True)

    def action_sync(self):
        if self.sync_type == 'document' and self.library_id:
            self.library_id.action_sync_now()
        elif self.sync_type == 'list' and self.list_id:
            self.list_id.action_sync_now()
        return {'type': 'ir.actions.act_window_close'}
