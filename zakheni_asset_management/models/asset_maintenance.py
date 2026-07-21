from odoo import api, fields, models


class AssetMaintenance(models.Model):
    _name = 'asset.maintenance'
    _description = 'Asset Maintenance'
    _order = 'planned_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    asset_id = fields.Many2one('asset.asset', string='Asset', required=True, ondelete='cascade')
    name = fields.Char(string='Subject', required=True, tracking=True)
    maintenance_type = fields.Selection([
        ('preventive', 'Preventive'),
        ('corrective', 'Corrective'),
    ], string='Type', default='preventive', required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='State', default='draft', required=True, tracking=True)
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Urgent'),
    ], string='Priority', default='1')
    planned_date = fields.Date(string='Planned Date', tracking=True)
    completed_date = fields.Date(string='Completed Date', readonly=True, tracking=True)
    assigned_to_id = fields.Many2one('res.users', string='Assigned To', tracking=True)
    cost = fields.Monetary(string='Cost', currency_field='currency_id')
    currency_id = fields.Many2one(related='asset_id.currency_id', string='Currency', readonly=True)
    vendor_id = fields.Many2one('res.partner', string='Service Vendor', domain=[('supplier_rank', '>', 0)])
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one(related='asset_id.company_id', string='Company', store=True, readonly=True)

    def action_plan(self):
        for rec in self:
            rec.state = 'planned'

    def action_start(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_complete(self):
        for rec in self:
            rec.write({
                'state': 'completed',
                'completed_date': fields.Date.today(),
            })

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
