# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrOrganization(models.Model):
    _name = 'hr.organization'
    _description = 'Organization'
    _order = 'name'
    _check_company_auto = True
    _sql_constraints = [
        ('hr_organization_name_company_uniq', 'unique(name, company_id)', 'An organization with this name already exists for this company.'),
    ]

    name = fields.Char(string='Organization', required=True, translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
    )

    @api.constrains('name', 'company_id')
    def _check_name_unique_ci(self):
        for organization in self:
            if not organization.name:
                continue
            domain = [
                ('id', '!=', organization.id),
                ('company_id', '=', organization.company_id.id if organization.company_id else False),
            ]
            # use ilike to catch case-insensitive duplicates
            if self.search_count(domain + [('name', 'ilike', organization.name.strip())], limit=1):
                raise ValidationError(_("An organization with this name already exists for this company."))
