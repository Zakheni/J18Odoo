from odoo import api, fields, models


class AssetLocation(models.Model):
    _name = 'asset.location'
    _description = 'Asset Location'
    _parent_store = True
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char()
    parent_id = fields.Many2one('asset.location', string='Parent Location', index=True, ondelete='cascade')
    child_ids = fields.One2many('asset.location', 'parent_id', string='Child Locations')
    parent_path = fields.Char(index=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    asset_count = fields.Integer(string='Assets', compute='_compute_asset_count', store=True)

    @api.depends('active')
    def _compute_asset_count(self):
        Asset = self.env['asset.asset']
        for loc in self:
            loc.asset_count = Asset.search_count([('current_location_id', '=', loc.id)])
