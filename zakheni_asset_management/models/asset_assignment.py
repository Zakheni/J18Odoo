from odoo import api, fields, models
from datetime import date


class AssetAssignment(models.Model):
    _name = 'asset.assignment'
    _description = 'Asset Assignment'
    _order = 'assigned_date desc, id desc'
    _rec_name = 'display_name'

    asset_id = fields.Many2one('asset.asset', string='Asset', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Assigned To', required=True)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True, readonly=True)
    assigned_date = fields.Date(string='Assigned Date', default=fields.Date.today, required=True)
    returned_date = fields.Date(string='Returned Date')
    state = fields.Selection([
        ('assigned', 'Assigned'),
        ('returned', 'Returned'),
    ], string='State', default='assigned', required=True)
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(related='asset_id.company_id', string='Company', store=True, readonly=True)

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    @api.depends('asset_id', 'employee_id', 'assigned_date')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f'{rec.asset_id.display_name} -> {rec.employee_id.name} ({rec.assigned_date})'

    def action_return(self):
        for rec in self:
            if rec.state == 'assigned':
                rec.write({
                    'state': 'returned',
                    'returned_date': fields.Date.today(),
                })
