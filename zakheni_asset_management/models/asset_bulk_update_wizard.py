from odoo import api, fields, models


class AssetBulkUpdateWizard(models.TransientModel):
    _name = 'asset.bulk.update.wizard'
    _description = 'Asset Bulk Update Wizard'

    asset_ids = fields.Many2many('asset.asset', string='Assets', required=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_use', 'In Use'),
        ('maintenance', 'Maintenance'),
        ('disposed', 'Disposed'),
    ], string='Status', required=True)
    current_location_id = fields.Many2one('asset.location', string='Location')
    assigned_employee_id = fields.Many2one('hr.employee', string='Assigned Employee')

    def action_apply(self):
        vals = {'status': self.status}
        if self.current_location_id:
            vals['current_location_id'] = self.current_location_id.id
        if self.assigned_employee_id:
            vals['assigned_employee_id'] = self.assigned_employee_id.id
        self.asset_ids.write(vals)
        return {'type': 'ir.actions.act_window_close'}
