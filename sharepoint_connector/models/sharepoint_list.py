import json
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class SharePointList(models.Model):
    _name = 'sharepoint.list'
    _description = 'SharePoint List Sync'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    site_id = fields.Many2one('sharepoint.site', string='SharePoint Site', required=True)
    list_name = fields.Char(string='SharePoint List Name', required=True)
    odoo_model = fields.Char(string='Odoo Model', required=True,
                             help='Technical name of the Odoo model to sync with')
    field_mapping = fields.Text(string='Field Mapping (JSON)',
                                help='JSON mapping: {"SharePointField": "odoo_field"}')
    external_id_field = fields.Char(string='External ID Field',
                                    help='Odoo field storing the SharePoint list item ID')
    last_sync_date = fields.Datetime(string='Last Sync')
    sync_direction = fields.Selection([
        ('bidirectional', 'Bidirectional'),
        ('odoo_to_sharepoint', 'Odoo → SharePoint'),
        ('sharepoint_to_odoo', 'SharePoint → Odoo'),
    ], string='Sync Direction', default='bidirectional', required=True)
    active = fields.Boolean(default=True)

    def get_mapping(self):
        if self.field_mapping:
            return json.loads(self.field_mapping)
        return {}

    def action_sync_now(self):
        for record in self:
            record._sync_list()
        return {'type': 'ir.actions.act_window_message', 'title': _('Sync Complete'), 'message': _('List sync completed.')}

    def _sync_list(self):
        pass

    def _odoo_to_sharepoint(self):
        pass

    def _sharepoint_to_odoo(self):
        pass

    def _run_scheduled_sync(self):
        lists = self.search([('active', '=', True)])
        for sp_list in lists:
            try:
                sp_list._sync_list()
            except Exception as e:
                _logger.error('Scheduled sync failed for list %s: %s', sp_list.name, e)
