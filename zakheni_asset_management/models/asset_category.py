from odoo import api, fields, models


class AssetCategory(models.Model):
    _name = 'asset.category'
    _description = 'Asset Category'
    _parent_store = True
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    code = fields.Char()
    parent_id = fields.Many2one('asset.category', string='Parent Category', index=True, ondelete='cascade')
    child_ids = fields.One2many('asset.category', 'parent_id', string='Child Categories')
    parent_path = fields.Char(index=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

    depreciation_method = fields.Selection([
        ('straight_line', 'Straight Line'),
        ('reducing_balance', 'Reducing Balance'),
    ], string='Default Depreciation Method', default='straight_line', required=True)
    depreciation_duration_months = fields.Integer(string='Default Duration (Months)', default=36, required=True)
    salvage_value_percent = fields.Float(string='Default Salvage %', default=10.0)
    default_location_id = fields.Many2one('asset.location', string='Default Location')

    asset_count = fields.Integer(string='Assets', compute='_compute_asset_count', store=True, recursive=True)

    @api.depends('child_ids.asset_count')
    def _compute_asset_count(self):
        Asset = self.env['asset.asset']
        for category in self:
            category.asset_count = Asset.search_count([('category_id', 'child_of', category.id)])

    def action_view_assets(self):
        self.ensure_one()
        assets = self.env['asset.asset'].search([('category_id', 'child_of', self.id)])
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assets',
            'view_mode': 'list,form',
            'res_model': 'asset.asset',
            'domain': [('id', 'in', assets.ids)],
        }


class AssetAssetStatus(models.Model):
    _name = 'asset.asset.status'
    _description = 'Asset Lifecycle Status'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    code = fields.Selection([
        ('draft', 'Draft'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
    ], required=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(default=False)
