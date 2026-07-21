from odoo import api, fields, models


class AssetAudit(models.Model):
    _name = 'asset.audit'
    _description = 'Asset Audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    display_name = fields.Char(string='Name', compute='_compute_display_name', store=True)
    name = fields.Char(string='Audit Reference', required=True, default='New', copy=False)
    date = fields.Date(string='Audit Date', default=fields.Date.today, required=True, tracking=True)
    location_id = fields.Many2one('asset.location', string='Location', tracking=True)
    include_sublocations = fields.Boolean(string='Include Sublocations', default=True)
    auditor_id = fields.Many2one('res.users', string='Auditor', default=lambda self: self.env.user, required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)
    line_ids = fields.One2many('asset.audit.line', 'audit_id', string='Audit Lines')
    total_count = fields.Integer(string='Total Assets', compute='_compute_counts', store=True)
    verified_count = fields.Integer(string='Verified', compute='_compute_counts', store=True)
    found_count = fields.Integer(string='Found', compute='_compute_counts', store=True)
    missing_count = fields.Integer(string='Missing', compute='_compute_counts', store=True)
    damage_count = fields.Integer(string='Damaged', compute='_compute_counts', store=True)
    moved_count = fields.Integer(string='Moved', compute='_compute_counts', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.depends('name', 'date')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.name} ({rec.date})" if rec.name and rec.date else rec.name or 'New'

    @api.depends('line_ids.verified', 'line_ids.asset_found', 'line_ids.condition', 'line_ids.new_location_id')
    def _compute_counts(self):
        for rec in self:
            lines = rec.line_ids
            rec.total_count = len(lines)
            rec.verified_count = len(lines.filtered('verified'))
            rec.found_count = len(lines.filtered('asset_found'))
            rec.missing_count = len(lines.filtered(lambda l: not l.asset_found))
            rec.damage_count = len(lines.filtered(lambda l: l.condition == 'damaged'))
            rec.moved_count = len(lines.filtered('new_location_id'))

    def action_prepare_assets(self):
        domain = []
        if self.location_id:
            if self.include_sublocations:
                domain.append(('current_location_id', 'child_of', self.location_id.id))
            else:
                domain.append(('current_location_id', '=', self.location_id.id))
        if not domain:
            domain.append(('status', 'not in', ('disposed',)))
        domain.append(('active', '=', True))

        assets = self.env['asset.asset'].search(domain)
        existing = self.line_ids.mapped('asset_id').ids
        to_create = assets - self.line_ids.mapped('asset_id')
        for asset in to_create:
            self.env['asset.audit.line'].create({
                'audit_id': self.id,
                'asset_id': asset.id,
                'expected_location_id': asset.current_location_id.id,
                'expected_employee_id': asset.assigned_employee_id.id,
            })
        return True

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_complete(self):
        self.write({'state': 'completed'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset(self):
        self.write({'state': 'draft'})


class AssetAuditLine(models.Model):
    _name = 'asset.audit.line'
    _description = 'Asset Audit Line'
    _order = 'audit_id, asset_id'
    _rec_name = 'asset_id'

    audit_id = fields.Many2one('asset.audit', string='Audit', required=True, ondelete='cascade')
    asset_id = fields.Many2one('asset.asset', string='Asset', required=True, ondelete='restrict')
    asset_code = fields.Char(related='asset_id.code', string='Asset Code', store=True)
    asset_name = fields.Char(related='asset_id.name', string='Asset Name', store=True)
    asset_barcode = fields.Char(related='asset_id.barcode', string='Barcode', store=True)
    asset_qr_code = fields.Binary(related='asset_id.qr_code', string='QR Code')
    expected_location_id = fields.Many2one('asset.location', string='Expected Location')
    scanned_location_id = fields.Many2one('asset.location', string='Scanned Location')
    new_location_id = fields.Many2one('asset.location', string='Move To Location')
    expected_employee_id = fields.Many2one('hr.employee', string='Expected Assignee')
    verified = fields.Boolean(string='Verified')
    verified_date = fields.Datetime(string='Verified On')
    verified_by = fields.Many2one('res.users', string='Verified By')
    asset_found = fields.Boolean(string='Asset Found', default=True)
    condition = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('damaged', 'Damaged'),
        ('unusable', 'Unusable'),
    ], string='Condition', default='good')
    notes = fields.Text(string='Notes')
    image = fields.Binary(string='Photo', attachment=True)

    scanned = fields.Char(string='Scan Barcode/QR')

    def action_scan_barcode(self):
        for rec in self:
            if not rec.scanned:
                continue
            code = rec.scanned.strip()
            barcode = rec.asset_id.barcode
            if code and (code == barcode or code == rec.asset_id.code):
                rec.write({
                    'verified': True,
                    'verified_date': fields.Datetime.now(),
                    'verified_by': self.env.user.id,
                    'asset_found': True,
                })
            rec.scanned = False
        return True

    def action_verify(self):
        for rec in self:
            rec.write({
                'verified': True,
                'verified_date': fields.Datetime.now(),
                'verified_by': self.env.user.id,
            })

    def action_mark_missing(self):
        self.write({
            'asset_found': False,
            'verified': True,
            'verified_date': fields.Datetime.now(),
            'verified_by': self.env.user.id,
        })

    def action_move_asset(self):
        for rec in self:
            if rec.new_location_id:
                rec.asset_id.write({'current_location_id': rec.new_location_id.id})
                rec.asset_id.message_post(
                    body=f"Asset moved to {rec.new_location_id.name} during audit {rec.audit_id.name}",
                )
