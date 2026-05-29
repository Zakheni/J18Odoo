# -*- coding: utf-8 -*-

from odoo import api, SUPERUSER_ID


def post_init_hook(cr_or_env, registry=None):
    # Odoo 17 calls post_init_hook with an Environment; older versions used (cr, registry).
    env = cr_or_env if hasattr(cr_or_env, "cr") else api.Environment(cr_or_env, SUPERUSER_ID, {})
    organization = env.ref('timesheet_analytics.hr_organization_no_categorized', raise_if_not_found=False)
    if not organization:
        return
    employees = env['hr.employee'].with_context(active_test=False).search([('organization_id', '=', False)])
    if employees:
        employees.write({'organization_id': organization.id})
    # Backfill timesheet lines from employee organization
    env.cr.execute(
        """
        UPDATE account_analytic_line AS aal
           SET organization_id = emp.organization_id
          FROM hr_employee AS emp
         WHERE aal.employee_id = emp.id
           AND aal.organization_id IS NULL
           AND emp.organization_id IS NOT NULL
        """
    )
