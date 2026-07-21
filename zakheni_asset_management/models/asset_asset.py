from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Asset(models.Model):
    _name = 'asset.asset'
    _description = 'Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code, name'
    _rec_name = 'display_name'

    def _default_company(self):
        return self.env.company

    def _default_currency(self):
        return self.env.company.currency_id

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    name = fields.Char(string='Asset Name', required=True, tracking=True)
    code = fields.Char(string='Asset Number', default=lambda self: self.env['ir.sequence'].next_by_code('zakheni.asset.asset') or 'NEW', readonly=True, copy=False, index=True)
    active = fields.Boolean(default=True, tracking=True)

    category_id = fields.Many2one('asset.category', string='Category', required=True, tracking=True)
    current_location_id = fields.Many2one('asset.location', string='Current Location', tracking=True)
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_storage', 'In Storage'),
        ('not_in_use', 'Not in Use'),
        ('in_use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('disposed', 'Disposed'),
    ], string='Status', default='draft', required=True, tracking=True)

    purchase_date = fields.Date(string='Purchase Date', default=fields.Date.today, tracking=True)
    purchase_value = fields.Monetary(string='Purchase Value', currency_field='currency_id', required=True, tracking=True)
    salvage_value = fields.Monetary(string='Salvage Value', currency_field='currency_id', compute='_compute_salvage_value', store=True, readonly=False, tracking=True)
    salvage_value_percent = fields.Float(string='Salvage %', default=10.0)
    book_value = fields.Monetary(string='Book Value', currency_field='currency_id', compute='_compute_book_value', store=True)
    cumulative_depreciation = fields.Monetary(string='Cumulative Depreciation', currency_field='currency_id', compute='_compute_book_value', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=_default_currency, required=True)
    company_id = fields.Many2one('res.company', string='Company', default=_default_company, required=True)

    supplier_id = fields.Many2one('res.partner', string='Supplier', domain=[('supplier_rank', '>', 0)], tracking=True)
    manufacturer = fields.Char(string='Manufacturer', tracking=True)
    model = fields.Char(string='Model', tracking=True)
    serial_number = fields.Char(string='Serial Number', tracking=True)
    barcode = fields.Char(string='Barcode', copy=False)
    license_plate = fields.Char(string='License Plate')
    warranty_expiry_date = fields.Date(string='Warranty Expiry', tracking=True)
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Image', attachment=True)

    depreciation_method = fields.Selection([
        ('straight_line', 'Straight Line'),
        ('reducing_balance', 'Reducing Balance'),
    ], string='Depreciation Method', default='straight_line', required=True, tracking=True)
    depreciation_duration_months = fields.Integer(string='Depreciation Duration (Months)', default=36, required=True, tracking=True)
    depreciation_start_date = fields.Date(string='Depreciation Start Date', default=fields.Date.today, tracking=True)

    depreciation_line_ids = fields.One2many('asset.depreciation.line', 'asset_id', string='Depreciation Schedule', copy=False)
    assignment_ids = fields.One2many('asset.assignment', 'asset_id', string='Assignment History', copy=False)
    maintenance_ids = fields.One2many('asset.maintenance', 'asset_id', string='Maintenance Records', copy=False)

    assigned_employee_id = fields.Many2one('hr.employee', string='Currently Assigned To', compute='_compute_current_assignment', store=True)
    assigned_date = fields.Date(string='Assigned Since', compute='_compute_current_assignment', store=True)

    @api.depends('name', 'code')
    def _compute_display_name(self):
        for asset in self:
            parts = [p for p in [asset.code, asset.name] if p]
            asset.display_name = ' - '.join(parts)

    @api.depends('purchase_value', 'salvage_value_percent')
    def _compute_salvage_value(self):
        for asset in self:
            if asset.purchase_value and asset.salvage_value_percent:
                asset.salvage_value = asset.purchase_value * asset.salvage_value_percent / 100.0
            elif not asset.salvage_value:
                asset.salvage_value = 0.0

    @api.depends('purchase_value', 'depreciation_line_ids.amount', 'salvage_value')
    def _compute_book_value(self):
        for asset in self:
            total_depr = sum(asset.depreciation_line_ids.mapped('amount'))
            asset.cumulative_depreciation = total_depr
            asset.book_value = max(asset.purchase_value - total_depr, asset.salvage_value or 0.0)

    @api.depends('assignment_ids.employee_id', 'assignment_ids.state', 'assignment_ids.assigned_date')
    def _compute_current_assignment(self):
        for asset in self:
            current = asset.assignment_ids.filtered(lambda a: a.state == 'assigned')
            if current:
                sorted_assignments = current.sorted(lambda a: a.assigned_date, reverse=True)
                asset.assigned_employee_id = sorted_assignments[0].employee_id
                asset.assigned_date = sorted_assignments[0].assigned_date
            else:
                asset.assigned_employee_id = False
                asset.assigned_date = False

    @api.onchange('category_id')
    def _onchange_category(self):
        if self.category_id:
            self.depreciation_method = self.category_id.depreciation_method
            self.depreciation_duration_months = self.category_id.depreciation_duration_months
            self.salvage_value_percent = self.category_id.salvage_value_percent
            if not self.current_location_id:
                self.current_location_id = self.category_id.default_location_id

    def action_mark_in_storage(self):
        self.write({'status': 'in_storage', 'assigned_employee_id': False})
        return {'type': 'ir.actions.act_window_close'}

    def action_mark_not_in_use(self):
        self.write({'status': 'not_in_use', 'assigned_employee_id': False})
        return {'type': 'ir.actions.act_window_close'}

    def action_mark_in_use(self):
        for rec in self:
            rec.write({'status': 'in_use', 'assigned_date': fields.Date.today()})
        return {'type': 'ir.actions.act_window_close'}

    def action_mark_maintenance(self):
        self.write({'status': 'maintenance'})
        return {'type': 'ir.actions.act_window_close'}

    def action_mark_disposed(self):
        self.write({'status': 'disposed'})
        return {'type': 'ir.actions.act_window_close'}

    def action_generate_depreciation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Generate Depreciation',
            'view_mode': 'form',
            'res_model': 'asset.depreciation.wizard',
            'target': 'new',
            'context': {'default_asset_id': self.id},
        }

    def action_view_assignments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Assignments',
            'view_mode': 'list,form',
            'res_model': 'asset.assignment',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }

    def action_view_maintenance(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance',
            'view_mode': 'list,form,kanban',
            'res_model': 'asset.maintenance',
            'domain': [('asset_id', '=', self.id)],
            'context': {'default_asset_id': self.id},
        }

    def action_print_barcode(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Print Barcode',
            'view_mode': 'form',
            'res_model': 'asset.asset',
            'res_id': self.id,
            'target': 'current',
        }

    @api.constrains('purchase_value', 'salvage_value')
    def _check_values(self):
        for asset in self:
            if asset.purchase_value <= 0:
                raise ValidationError('Purchase value must be positive.')
            if asset.salvage_value and asset.salvage_value >= asset.purchase_value:
                raise ValidationError('Salvage value must be less than purchase value.')
