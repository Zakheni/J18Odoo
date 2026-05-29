from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    organization_id = fields.Many2one(
        'hr.organization',
        string='Organization',
        compute='_compute_organization_id',
        store=True,
        readonly=True,
        compute_sudo=True,
        check_company=True,
    )

    @api.depends('employee_id', 'employee_id.organization_id')
    def _compute_organization_id(self):
        for line in self:
            line.organization_id = line.employee_id.organization_id
