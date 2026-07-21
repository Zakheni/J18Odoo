from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_asset_manager = fields.Boolean(string='Full Asset Management', implied_group='base.group_system', default=True)
    group_asset_user = fields.Boolean(string='Asset User (Read)', implied_group='base.group_user', default=True)
    asset_depreciation_default_method = fields.Selection([
        ('straight_line', 'Straight Line'),
        ('reducing_balance', 'Reducing Balance'),
    ], string='Default Depreciation Method', default='straight_line', config_parameter='zakheni_asset.depreciation_default_method')
    asset_barcode_format = fields.Selection([
        ('code128', 'Code 128'),
        ('qr', 'QR Code'),
    ], string='Asset Label Format', default='qr', config_parameter='zakheni_asset.barcode_format')
