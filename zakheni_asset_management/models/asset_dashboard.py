from odoo import api, fields, models


class AssetDashboard(models.TransientModel):
    _name = 'asset.dashboard'
    _description = 'Asset Dashboard'

    total_assets = fields.Integer(string='Total Assets')
    total_purchase_value = fields.Monetary(string='Total Purchase Value', currency_field='currency_id')
    total_book_value = fields.Monetary(string='Total Book Value', currency_field='currency_id')
    total_depreciation = fields.Monetary(string='Total Depreciation', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id)
    in_use_count = fields.Integer(string='In Use')
    maintenance_count = fields.Integer(string='Under Maintenance')
    disposed_count = fields.Integer(string='Disposed')
    draft_count = fields.Integer(string='Draft')
    it_count = fields.Integer(string='IT Equipment')
    furniture_count = fields.Integer(string='Furniture')
    vehicle_count = fields.Integer(string='Vehicles')
    building_count = fields.Integer(string='Buildings')

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        self = self.new(res)
        self.action_compute()
        res.update({
            'total_assets': self.total_assets,
            'total_purchase_value': self.total_purchase_value,
            'total_book_value': self.total_book_value,
            'total_depreciation': self.total_depreciation,
            'in_use_count': self.in_use_count,
            'maintenance_count': self.maintenance_count,
            'disposed_count': self.disposed_count,
            'draft_count': self.draft_count,
            'it_count': self.it_count,
            'furniture_count': self.furniture_count,
            'vehicle_count': self.vehicle_count,
            'building_count': self.building_count,
        })
        return res

    def action_compute(self):
        Asset = self.env['asset.asset']
        all_assets = Asset.search([])

        self.total_assets = len(all_assets)
        self.total_purchase_value = sum(all_assets.mapped('purchase_value'))
        self.total_book_value = sum(all_assets.mapped('book_value'))
        self.total_depreciation = sum(all_assets.mapped('cumulative_depreciation'))
        self.in_use_count = Asset.search_count([('status', '=', 'in_use')])
        self.maintenance_count = Asset.search_count([('status', '=', 'maintenance')])
        self.disposed_count = Asset.search_count([('status', '=', 'disposed')])
        self.draft_count = Asset.search_count([('status', '=', 'draft')])

        it_cat = self.env.ref('zakheni_asset_management.asset_cat_it', raise_if_not_found=False)
        furn_cat = self.env.ref('zakheni_asset_management.asset_cat_furniture', raise_if_not_found=False)
        veh_cat = self.env.ref('zakheni_asset_management.asset_cat_vehicle', raise_if_not_found=False)
        bldg_cat = self.env.ref('zakheni_asset_management.asset_cat_building', raise_if_not_found=False)

        if it_cat:
            self.it_count = Asset.search_count([('category_id', '=', it_cat.id)])
        if furn_cat:
            self.furniture_count = Asset.search_count([('category_id', '=', furn_cat.id)])
        if veh_cat:
            self.vehicle_count = Asset.search_count([('category_id', '=', veh_cat.id)])
        if bldg_cat:
            self.building_count = Asset.search_count([('category_id', '=', bldg_cat.id)])
