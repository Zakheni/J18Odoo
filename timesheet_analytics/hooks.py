from odoo import api, SUPERUSER_ID


def post_init_hook(cr_or_env, registry=None):
    env = cr_or_env if hasattr(cr_or_env, "cr") else api.Environment(cr_or_env, SUPERUSER_ID, {})

    # Set the root Timesheets menu to open the custom dashboard
    menu = env.ref('hr_timesheet.timesheet_menu_root', raise_if_not_found=False)
    dashboard_action = env.ref('timesheet_analytics.timesheet_dashboard_action_client', raise_if_not_found=False)
    if menu and dashboard_action:
        menu.action = f"ir.actions.client,{dashboard_action.id}"

    organization = env.ref('timesheet_analytics.hr_organization_no_categorized', raise_if_not_found=False)
    if not organization:
        return
    employees = env['hr.employee'].with_context(active_test=False).search([('organization_id', '=', False)])
    if employees:
        employees.write({'organization_id': organization.id})
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
