from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _default_organization_id(self):
        organization = self.env.ref('timesheet_analytics.hr_organization_no_categorized', raise_if_not_found=False)
        return organization.id if organization else False

    organization_id = fields.Many2one(
        'hr.organization',
        string='Organization',
        default=_default_organization_id,
        domain="[('company_id', 'in', [False, company_id])]",
        check_company=True,
    )
