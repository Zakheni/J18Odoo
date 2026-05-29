# -*- coding: utf-8 -*-

from datetime import date
import json

from odoo import fields
from odoo.http import request, route
from odoo.osv import expression
from odoo.tools import date_utils

from odoo.addons.timesheet_analytics.controllers.timesheet_dashboard import TimesheetDashBoard


class WebsiteTimesheetAnalytics(TimesheetDashBoard):

    def _get_linked_employee(self):
        user = request.env.user
        employee = request.env['hr.employee'].sudo().search([('user_id', '=', user.id)], limit=1)
        return employee

    def _build_portal_filter_context(self, employee, project_id=False, task_id=False, organization_id=False,
                                     year=False, month=False, date_from=False, date_to=False):
        company_ids = request.env.companies.ids

        project_ids = self._normalize_ids(project_id)
        task_ids = self._normalize_ids(task_id)
        organization_ids = self._normalize_ids(organization_id)

        base_domain = [
            ('company_id', 'in', company_ids),
            ('project_id', '!=', False),
            ('employee_id', '=', employee.id),
        ]

        project_domain = [('project_id', 'in', project_ids)] if project_ids else []
        task_domain = [('task_id', 'in', task_ids)] if task_ids else []
        organization_domain = [('organization_id', 'in', organization_ids)] if organization_ids else []
        all_entity_domains = project_domain + task_domain + organization_domain

        request.env.flush_all()
        analytic_line_model = request.env['account.analytic.line'].sudo()

        domain_core_date = list(base_domain)
        domain_months_date = list(base_domain)
        domain_year_options = list(base_domain) + all_entity_domains

        year_groups = analytic_line_model._read_group(
            domain=domain_year_options,
            groupby=['date:year'],
            aggregates=['id:count'],
        )
        years_set = set()
        for group in year_groups:
            year_value = self._extract_date_value(group[0])
            if year_value:
                years_set.add(year_value.year)
        available_years = sorted(years_set)

        year_int = self._safe_int(year)
        if year_int and year_int in available_years:
            year_start = date(year_int, 1, 1)
            year_end = date(year_int, 12, 31)
            domain_core_date += [('date', '>=', year_start), ('date', '<=', year_end)]
            domain_months_date += [('date', '>=', year_start), ('date', '<=', year_end)]
        else:
            year_int = False

        month_int = self._safe_int(month)
        if month_int and not 1 <= month_int <= 12:
            month_int = False

        if month_int:
            if year_int:
                month_start = date(year_int, month_int, 1)
                month_end = date_utils.end_of(month_start, 'month')
                domain_core_date += [('date', '>=', month_start), ('date', '<=', month_end)]
            elif available_years:
                month_domains = []
                for year_value in available_years:
                    month_start = date(year_value, month_int, 1)
                    month_end = date_utils.end_of(month_start, 'month')
                    month_domains.append([('date', '>=', month_start), ('date', '<=', month_end)])
                domain_core_date = expression.AND([domain_core_date, expression.OR(month_domains)])
            else:
                month_int = False

        month_groups = analytic_line_model._read_group(
            domain=list(domain_months_date) + all_entity_domains,
            groupby=['date:month'],
            aggregates=['id:count'],
        )
        months_set = set()
        for group in month_groups:
            month_value = self._extract_date_value(group[0])
            if month_value:
                months_set.add(month_value.month)
        available_months = sorted(months_set)

        min_date = max_date = False
        min_max_groups = analytic_line_model._read_group(
            domain=list(domain_core_date) + all_entity_domains,
            aggregates=['date:min', 'date:max'],
        )
        if min_max_groups:
            min_date, max_date = min_max_groups[0]

        available_date_min = fields.Date.to_string(min_date) if min_date else False
        available_date_max = fields.Date.to_string(max_date) if max_date else False

        from_date = self._safe_to_date(date_from)
        to_date = self._safe_to_date(date_to)
        if from_date and to_date and from_date > to_date:
            from_date, to_date = to_date, from_date

        date_domain = []
        if from_date:
            date_domain.append(('date', '>=', from_date))
        if to_date:
            date_domain.append(('date', '<=', to_date))

        full_domain = list(domain_core_date) + all_entity_domains + date_domain

        return {
            'project_domain': project_domain,
            'task_domain': task_domain,
            'organization_domain': organization_domain,
            'domain_core_date': domain_core_date,
            'date_domain': date_domain,
            'full_domain': full_domain,
            'available_years': available_years,
            'available_months': available_months,
            'available_date_min': available_date_min,
            'available_date_max': available_date_max,
            'employee_id': employee.id,
        }

    @route('/my/timesheet-analytics', type='http', auth='user', website=True)
    def portal_timesheet_analytics(self, **kwargs):
        employee = self._get_linked_employee()
        values = {
            'page_name': 'timesheet_analytics',
            'has_linked_employee': bool(employee),
        }
        return request.render('web_timesheet_analytics.portal_timesheet_analytics_page', values)

    @route('/get/project/data', auth='user', type='json')
    def fetch_project_data(self, project_id=False, task_id=False, employee_id=False, organization_id=False,
                           year=False, month=False, date_from=False, date_to=False):
        user = request.env.user
        if user.has_group('base.group_portal'):
            employee = self._get_linked_employee()
            employee_id = [employee.id] if employee else []
            data = super().fetch_project_data(
                project_id=project_id,
                task_id=task_id,
                employee_id=employee_id,
                organization_id=organization_id,
                year=year,
                month=month,
                date_from=date_from,
                date_to=date_to,
            )
            data['employees'] = [{'id': employee.id, 'name': employee.name}] if employee else []
            data['employees_ids'] = [employee.id] if employee else []
            return data
        return super().fetch_project_data(
            project_id=project_id,
            task_id=task_id,
            employee_id=employee_id,
            organization_id=organization_id,
            year=year,
            month=month,
            date_from=date_from,
            date_to=date_to,
        )

    @route('/timesheet_analytics/export/xlsx', type='http', auth='user')
    def export_timesheet_xlsx(self, data=None, **kw):
        if request.env.user.has_group('base.group_portal'):
            employee = self._get_linked_employee()
            try:
                params = json.loads(data) if data else {}
            except Exception:
                params = {}
            params['employee_id'] = [employee.id] if employee else []
            data = json.dumps(params)
        return super().export_timesheet_xlsx(data=data, **kw)

    @route('/timesheet_analytics/export/pivot/presets/xlsx', type='http', auth='user')
    def export_timesheet_pivot_presets_xlsx(self, data=None, **kw):
        if request.env.user.has_group('base.group_portal'):
            employee = self._get_linked_employee()
            try:
                params = json.loads(data) if data else {}
            except Exception:
                params = {}
            params['employee_id'] = [employee.id] if employee else []
            data = json.dumps(params)
        return super().export_timesheet_pivot_presets_xlsx(data=data, **kw)


    @route('/my/timesheet-analytics/data', type='json', auth='user')
    def portal_timesheet_analytics_data(self, project_id=False, task_id=False, employee_id=False, organization_id=False,
                                        year=False, month=False, date_from=False, date_to=False):
        employee = self._get_linked_employee()
        if not employee:
            return {
                'projects_count': 0,
                'tasks_count': 0,
                'employees_count': 0,
                'organizations_count': 0,
                'timesheets_count': 0,
                'total_hours': 0.0,
                'projects': [],
                'tasks': [],
                'employees': [],
                'projects_ids': [],
                'tasks_ids': [],
                'employees_ids': [],
                'organizations': [],
                'available_years': [],
                'available_months': [],
                'available_date_min': False,
                'available_date_max': False,
                'charts': {
                    'hours_per_employee': [],
                    'hours_over_time': [],
                    'hours_per_project': [],
                    'hours_per_organization': [],
                    'employee_task_breakdown': {},
                    'project_task_breakdown': {},
                    'day_breakdown': {},
                },
                'timesheet_rows': [],
                'employee_name': False,
            }

        filter_context = self._build_portal_filter_context(
            employee=employee,
            project_id=project_id,
            task_id=task_id,
            organization_id=organization_id,
            year=year,
            month=month,
            date_from=date_from,
            date_to=date_to,
        )

        analytic_line_model = request.env['account.analytic.line'].sudo()
        timesheets = analytic_line_model.search(filter_context['full_domain'], order='date desc, id desc')

        project_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['task_domain']
            + filter_context['organization_domain']
            + filter_context['date_domain']
        )
        task_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['project_domain']
            + filter_context['organization_domain']
            + filter_context['date_domain']
        )
        organization_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['project_domain']
            + filter_context['task_domain']
            + filter_context['date_domain']
            + [('organization_id', '!=', False)]
        )

        projects = [
            group[0] for group in analytic_line_model._read_group(
                domain=project_options_domain,
                groupby=['project_id'],
                aggregates=['id:count'],
            ) if group and group[0]
        ]
        tasks = [
            group[0] for group in analytic_line_model._read_group(
                domain=task_options_domain,
                groupby=['task_id'],
                aggregates=['id:count'],
            ) if group and group[0]
        ]
        organizations = [
            group[0] for group in analytic_line_model._read_group(
                domain=organization_options_domain,
                groupby=['organization_id'],
                aggregates=['id:count'],
            ) if group and group[0]
        ]

        projects_data = [
            {
                'id': project.id,
                'name': project.name,
            }
            for project in sorted(projects, key=lambda item: (item.name or '').lower())
        ]
        tasks_data = [
            {
                'id': task.id,
                'name': task.name,
            }
            for task in sorted(tasks, key=lambda item: (item.name or '').lower())
        ]
        organizations_data = [
            {
                'id': organization.id,
                'name': organization.name,
            }
            for organization in sorted(organizations, key=lambda item: (item.name or '').lower())
        ]

        filtered_projects = timesheets.mapped('project_id').filtered(lambda record: record.id)
        filtered_tasks = timesheets.mapped('task_id').filtered(lambda record: record.id)
        filtered_organizations = timesheets.mapped('organization_id').filtered(lambda record: record.id)

        return {
            'projects_count': len(filtered_projects),
            'tasks_count': len(filtered_tasks),
            'employees_count': 1,
            'organizations_count': len(filtered_organizations),
            'timesheets_count': len(timesheets),
            'total_hours': sum(timesheets.mapped('unit_amount')) if timesheets else 0.0,
            'projects': projects_data,
            'tasks': tasks_data,
            'employees': [{'id': employee.id, 'name': employee.name}],
            'projects_ids': [project['id'] for project in projects_data],
            'tasks_ids': [task['id'] for task in tasks_data],
            'employees_ids': [employee.id],
            'organizations': organizations_data,
            'available_years': filter_context['available_years'],
            'available_months': filter_context['available_months'],
            'available_date_min': filter_context['available_date_min'],
            'available_date_max': filter_context['available_date_max'],
            'charts': self._build_chart_payload(analytic_line_model, filter_context['full_domain']),
            'timesheet_rows': self._serialize_timesheet_rows(timesheets),
            'employee_name': employee.name,
        }
