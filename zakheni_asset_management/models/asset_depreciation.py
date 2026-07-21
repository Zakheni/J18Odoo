from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class AssetDepreciationLine(models.Model):
    _name = 'asset.depreciation.line'
    _description = 'Asset Depreciation Line'
    _order = 'date, id'

    asset_id = fields.Many2one('asset.asset', string='Asset', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True)
    amount = fields.Monetary(string='Depreciation Amount', currency_field='currency_id', required=True)
    cumulative_amount = fields.Monetary(string='Cumulative Amount', currency_field='currency_id', compute='_compute_cumulative', store=True)
    remaining_value = fields.Monetary(string='Remaining Value', currency_field='currency_id', compute='_compute_cumulative', store=True)
    currency_id = fields.Many2one(related='asset_id.currency_id', string='Currency', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
    ], string='State', default='draft', required=True)
    notes = fields.Char(string='Notes')
    company_id = fields.Many2one(related='asset_id.company_id', string='Company', store=True, readonly=True)

    @api.depends('amount', 'asset_id.purchase_value', 'asset_id.salvage_value')
    def _compute_cumulative(self):
        for line in self:
            lines_before = line.asset_id.depreciation_line_ids.filtered(
                lambda l: l.date < line.date or (l.date == line.date and l.id <= line.id)
            )
            cumulative = sum(lines_before.mapped('amount'))
            line.cumulative_amount = cumulative
            line.remaining_value = max(line.asset_id.purchase_value - cumulative, line.asset_id.salvage_value or 0.0)

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'


class AssetDepreciationWizard(models.TransientModel):
    _name = 'asset.depreciation.wizard'
    _description = 'Generate Depreciation Schedule'

    asset_id = fields.Many2one('asset.asset', string='Asset', required=True)
    date_from = fields.Date(string='Start Date', required=True, default=fields.Date.today)
    date_to = fields.Date(string='End Date', required=True)
    force_regenerate = fields.Boolean(string='Replace Existing Lines', default=False)

    def action_generate(self):
        self.ensure_one()
        asset = self.asset_id
        lines = self.env['asset.depreciation.line']

        if self.force_regenerate:
            asset.depreciation_line_ids.unlink()

        existing_dates = set(asset.depreciation_line_ids.mapped('date'))
        depr_base = asset.purchase_value - asset.salvage_value
        if depr_base <= 0:
            raise ValidationError('No depreciable base (purchase value - salvage value = 0).')

        current_date = self.date_from
        monthly_amount = depr_base / asset.depreciation_duration_months

        while current_date <= self.date_to:
            if current_date not in existing_dates:
                if asset.depreciation_method == 'reducing_balance':
                    annual_rate = 2.0 / (asset.depreciation_duration_months / 12.0) if asset.depreciation_duration_months else 0.0
                    monthly_rate = annual_rate / 12.0
                    lines_before = asset.depreciation_line_ids.filtered(lambda l: l.date < current_date)
                    already_depreciated = sum(lines_before.mapped('amount'))
                    remaining = asset.purchase_value - already_depreciated - asset.salvage_value
                    amount = max(remaining * monthly_rate, 0.0)
                else:
                    amount = monthly_amount

                if amount < 0.01:
                    break

                lines.create({
                    'asset_id': asset.id,
                    'date': current_date,
                    'amount': round(amount, 2),
                    'state': 'draft',
                })
            current_date = current_date + relativedelta(months=1)

        return {'type': 'ir.actions.act_window_close'}
