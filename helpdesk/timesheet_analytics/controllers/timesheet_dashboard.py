# -*- coding: utf-8 -*-

import base64
import io
import json
import logging
from datetime import date, datetime

from werkzeug.datastructures import FileStorage

from odoo import fields
from odoo.http import Controller, content_disposition, request, route
from odoo.osv import expression
from odoo.tools import date_utils, osutil
from odoo.tools.misc import xlsxwriter

_logger = logging.getLogger(__name__)


class TimesheetDashBoard(Controller):
    EXPORT_COLUMN_DEFINITIONS = {
        'date': {'label': 'Date', 'width': 14},
        'year': {'label': 'Year', 'width': 10},
        'month': {'label': 'Month', 'width': 12},
        'employee': {'label': 'Employee', 'width': 22},
        'organization': {'label': 'Organization', 'width': 22},
        'project': {'label': 'Project', 'width': 24},
        'task': {'label': 'Task', 'width': 24},
        'description': {'label': 'Description', 'width': 48},
        'hours': {'label': 'Hours', 'width': 12},
        'user': {'label': 'Timesheet User', 'width': 22},
        'company': {'label': 'Company', 'width': 20},
    }
    DEFAULT_EXPORT_COLUMNS = ['date', 'year', 'month', 'employee', 'organization', 'project', 'task', 'description', 'hours']
    MONTH_LABELS = {
        1: 'January',
        2: 'February',
        3: 'March',
        4: 'April',
        5: 'May',
        6: 'June',
        7: 'July',
        8: 'August',
        9: 'September',
        10: 'October',
        11: 'November',
        12: 'December',
    }

    PIVOT_PRESETS = {
        # key: {sheet_name, groupby, columns}
        'employee_totals': {
            'sheet': 'Employee Hours Summary',
            'groupby': ['employee_id'],
            'columns': ['Employee', 'Total Hours'],
        },
        'project_totals': {
            'sheet': 'Project Hours Summary',
            'groupby': ['project_id'],
            'columns': ['Project', 'Total Hours'],
        },
        'task_by_project': {
            'sheet': 'Task Analysis - Project',
            'groupby': ['project_id', 'task_id'],
            'columns': ['Project', 'Task', 'Total Hours'],
        },
        'task_by_employee': {
            'sheet': 'Task Analysis - Employee',
            'groupby': ['employee_id', 'task_id'],
            'columns': ['Employee', 'Task', 'Total Hours'],
        },
        'monthly_summaries': {
            'sheet': 'Monthly Hours Summary',
            'groupby': ['date:year', 'date:month'],
            'columns': ['Year', 'Month', 'Total Hours'],
        },
        'org_insights': {
            'sheet': 'Organization Monthly Insights',
            'groupby': ['organization_id', 'date:year', 'date:month'],
            'columns': ['Organization', 'Year', 'Month', 'Total Hours'],
        },
        'employee_project_month': {
            'sheet': 'Employee-Project Monthly',
            'groupby': ['employee_id', 'project_id', 'date:year', 'date:month'],
            'columns': ['Employee', 'Project', 'Year', 'Month', 'Total Hours'],
        },
    }

    SOURCE_SHEET_HEADERS = [
        ('Organization', 24),
        ('Project', 28),
        ('Task', 28),
        ('Employee', 22),
        ('Expenditure Type', 18),
        ('Year', 10),
        ('Month', 14),
        ('Hours', 12),
    ]

    def _get_pivot_preset(self, key):
        preset = self.PIVOT_PRESETS.get(str(key or '').strip())
        return preset if preset else False

    def _get_expenditure_label(self, line):
        # optional field (from web_timesheet)
        if not hasattr(line, 'expenditure_type') or not getattr(line, 'expenditure_type', False):
            return ''
        try:
            selection = dict(line._fields['expenditure_type'].selection)
            return selection.get(line.expenditure_type, '') or ''
        except Exception:
            return ''

    def _export_source_sheet(self, workbook, filter_context):
        analytic_line_model = request.env['account.analytic.line']
        timesheets = analytic_line_model.search(filter_context['full_domain'], order='date asc, id asc')

        header_style = workbook.add_format({
            'bold': True,
            'font_color': '#FFFFFF',
            'bg_color': '#4F46E5',
            'border': 1,
            'border_color': '#4338CA',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        cell_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'text_wrap': True,
            'valign': 'top',
        })
        hours_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'num_format': '#,##0.00',
            'align': 'right',
            'valign': 'top',
        })

        source_ws = workbook.add_worksheet('Source Data')
        for cidx, (label, width) in enumerate(self.SOURCE_SHEET_HEADERS):
            source_ws.set_column(cidx, cidx, width)
            source_ws.write(0, cidx, label, header_style)
        source_ws.freeze_panes(1, 0)

        for ridx, line in enumerate(timesheets, start=1):
            source_ws.write(ridx, 0, line.organization_id.name if line.organization_id else '', cell_style)
            source_ws.write(ridx, 1, line.project_id.name if line.project_id else '', cell_style)
            source_ws.write(ridx, 2, line.task_id.name if line.task_id else '', cell_style)
            source_ws.write(ridx, 3, line.employee_id.name if line.employee_id else '', cell_style)
            source_ws.write(ridx, 4, self._get_expenditure_label(line), cell_style)
            source_ws.write(ridx, 5, line.date.year if line.date else '', cell_style)
            source_ws.write(ridx, 6, self.MONTH_LABELS.get(line.date.month, '') if line.date else '', cell_style)
            source_ws.write(ridx, 7, float(line.unit_amount or 0.0), hours_style)

        last_row = len(timesheets) + 1  # include header row
        last_col = len(self.SOURCE_SHEET_HEADERS) - 1
        return {
            'worksheet': source_ws,
            'last_row': last_row,
            'last_col': last_col,
            'hours_style': hours_style,
        }

    def _add_pivot_preset_sheet(self, workbook, filter_context, preset_key, preset, hours_style):
        safe_sheet = (preset.get('sheet') or str(preset_key) or 'Pivot')[:31]
        ws = workbook.add_worksheet(safe_sheet)

        header_style = workbook.add_format({
            'bold': True,
            'font_color': '#FFFFFF',
            'bg_color': '#4F46E5',
            'border': 1,
            'border_color': '#4338CA',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })
        cell_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'text_wrap': True,
            'valign': 'top',
        })

        columns = preset.get('columns') or []
        for cidx, label in enumerate(columns):
            ws.set_column(cidx, cidx, 22)
            ws.write(0, cidx, label, header_style)
        ws.freeze_panes(1, 0)

        analytic_line_model = request.env['account.analytic.line']
        groups = analytic_line_model._read_group(
            domain=filter_context['full_domain'],
            groupby=preset.get('groupby') or [],
            aggregates=['unit_amount:sum'],
        )

        def _as_name(v):
            return v.name if hasattr(v, 'name') and v else ''

        rows = []
        # We aggregate by display name for "unique project names" requirement.
        # This also ensures totals sum across all tasks within the same named project.
        accumulator = {}
        for group in groups:
            gb_values = group[:-1]
            total = float(group[-1] or 0.0)
            if not total:
                continue

            if preset_key == 'employee_totals':
                employee_name = _as_name(gb_values[0])
                accumulator[(employee_name,)] = accumulator.get((employee_name,), 0.0) + total
            elif preset_key == 'project_totals':
                project_name = _as_name(gb_values[0])
                accumulator[(project_name,)] = accumulator.get((project_name,), 0.0) + total
            elif preset_key == 'task_by_project':
                project_name = _as_name(gb_values[0])
                task_name = _as_name(gb_values[1])
                accumulator[(project_name, task_name)] = accumulator.get((project_name, task_name), 0.0) + total
            elif preset_key == 'task_by_employee':
                employee_name = _as_name(gb_values[0])
                task_name = _as_name(gb_values[1])
                accumulator[(employee_name, task_name)] = accumulator.get((employee_name, task_name), 0.0) + total
            elif preset_key == 'monthly_summaries':
                year_val = self._extract_date_value(gb_values[0])
                month_val = self._extract_date_value(gb_values[1])
                year_label = year_val.year if year_val else ''
                month_label = self.MONTH_LABELS.get(month_val.month, '') if month_val else ''
                accumulator[(year_label, month_label)] = accumulator.get((year_label, month_label), 0.0) + total
            elif preset_key == 'org_insights':
                org = gb_values[0]
                year_val = self._extract_date_value(gb_values[1])
                month_val = self._extract_date_value(gb_values[2])
                org_name = _as_name(org)
                year_label = year_val.year if year_val else ''
                month_label = self.MONTH_LABELS.get(month_val.month, '') if month_val else ''
                accumulator[(org_name, year_label, month_label)] = accumulator.get((org_name, year_label, month_label), 0.0) + total
            elif preset_key == 'employee_project_month':
                employee = gb_values[0]
                project = gb_values[1]
                year_val = self._extract_date_value(gb_values[2])
                month_val = self._extract_date_value(gb_values[3])
                employee_name = _as_name(employee)
                project_name = _as_name(project)
                year_label = year_val.year if year_val else ''
                month_label = self.MONTH_LABELS.get(month_val.month, '') if month_val else ''
                accumulator[(employee_name, project_name, year_label, month_label)] = accumulator.get(
                    (employee_name, project_name, year_label, month_label), 0.0
                ) + total

        for key_tuple, total in accumulator.items():
            rows.append(tuple(key_tuple) + (total,))

        # Sort outputs for consistent analytics feel
        rows.sort(key=lambda r: tuple(str(x).lower() for x in r[:-1]) + (0,))

        for ridx, row in enumerate(rows, start=1):
            for cidx, value in enumerate(row):
                if cidx == len(row) - 1:
                    ws.write(ridx, cidx, value, hours_style)
                else:
                    ws.write(ridx, cidx, value, cell_style)

    def _export_pivot_presets_xlsx(self, filter_context, preset_keys):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        source_info = self._export_source_sheet(workbook, filter_context)
        seen = set()
        for key in preset_keys:
            preset = self._get_pivot_preset(key)
            if not preset:
                continue
            if key in seen:
                continue
            seen.add(key)
            self._add_pivot_preset_sheet(
                workbook,
                filter_context,
                key,
                preset,
                source_info['hours_style'],
            )

        workbook.close()
        return output.getvalue()


    def _normalize_ids(self, values):
        if values in (False, None, "", "all"):
            return []
        if not isinstance(values, (list, tuple, set)):
            values = [values]

        normalized = []
        for value in values:
            if value in (False, None, "", "all"):
                continue
            try:
                value_int = int(value)
            except (TypeError, ValueError):
                continue
            if value_int > 0 and value_int not in normalized:
                normalized.append(value_int)
        return normalized

    def _safe_int(self, value):
        if value in (False, None, "", "all"):
            return False
        try:
            return int(value)
        except (TypeError, ValueError):
            return False

    def _safe_to_date(self, value):
        if not value:
            return False
        try:
            return fields.Date.to_date(value)
        except (TypeError, ValueError):
            return False

    def _extract_date_value(self, value):
        if isinstance(value, (date, datetime)):
            return value
        return fields.Date.to_date(value)

    def _build_filter_context(self, project_id=False, task_id=False, employee_id=False, organization_id=False, year=False, month=False, date_from=False, date_to=False):
        user = request.env.user
        company_ids = request.env.companies.ids

        project_ids = self._normalize_ids(project_id)
        task_ids = self._normalize_ids(task_id)
        employee_ids = self._normalize_ids(employee_id)
        organization_ids = self._normalize_ids(organization_id)

        base_domain = [
            ('company_id', 'in', company_ids),
            ('project_id', '!=', False),
        ]

        if not user.has_group('hr_timesheet.group_hr_timesheet_user'):
            base_domain.append(('user_id', '=', user.id))

        project_domain = [('project_id', 'in', project_ids)] if project_ids else []
        task_domain = [('task_id', 'in', task_ids)] if task_ids else []
        employee_domain = [('employee_id', 'in', employee_ids)] if employee_ids else []
        organization_domain = [('organization_id', 'in', organization_ids)] if organization_ids else []
        all_entity_domains = project_domain + task_domain + employee_domain + organization_domain

        request.env.flush_all()
        analytic_line_model = request.env['account.analytic.line']

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
            'project_ids': project_ids,
            'task_ids': task_ids,
            'employee_ids': employee_ids,
            'organization_ids': organization_ids,
            'project_domain': project_domain,
            'task_domain': task_domain,
            'employee_domain': employee_domain,
            'organization_domain': organization_domain,
            'all_entity_domains': all_entity_domains,
            'domain_core_date': domain_core_date,
            'domain_months_date': domain_months_date,
            'date_domain': date_domain,
            'full_domain': full_domain,
            'available_years': available_years,
            'available_months': available_months,
            'available_date_min': available_date_min,
            'available_date_max': available_date_max,
            'selected_year': year_int,
            'selected_month': month_int,
            'date_from': from_date,
            'date_to': to_date,
        }

    def _normalize_export_columns(self, columns):
        if not isinstance(columns, (list, tuple)):
            columns = []

        normalized = []
        for column in columns:
            key = str(column or '').strip()
            if key in self.EXPORT_COLUMN_DEFINITIONS and key not in normalized:
                normalized.append(key)

        return normalized or list(self.DEFAULT_EXPORT_COLUMNS)

    def _get_column_value(self, line, column_key):
        if column_key == 'date':
            return line.date or ''
        if column_key == 'year':
            return line.date.year if line.date else ''
        if column_key == 'month':
            if not line.date:
                return ''
            month_int = line.date.month
            return self.MONTH_LABELS.get(month_int, month_int)
        if column_key == 'employee':
            return line.employee_id.name or ''
        if column_key == 'organization':
            return line.organization_id.name or ''
        if column_key == 'project':
            return line.project_id.name or ''
        if column_key == 'task':
            return line.task_id.name or ''
        if column_key == 'description':
            return line.name or ''
        if column_key == 'hours':
            return line.unit_amount or 0.0
        if column_key == 'user':
            return line.user_id.name or ''
        if column_key == 'company':
            return line.company_id.name or ''
        return ''

    def _serialize_timesheet_rows(self, timesheets):
        rows = []
        for line in timesheets:
            rows.append({
                'id': line.id,
                'date': fields.Date.to_string(line.date) if line.date else '',
                'year': line.date.year if line.date else False,
                'month': line.date.month if line.date else False,
                'employee': line.employee_id.name or '',
                'organization': line.organization_id.name or '',
                'project': line.project_id.name or '',
                'task': line.task_id.name or '',
                'description': line.name or '',
                'hours': float(line.unit_amount or 0.0),
                'user': line.user_id.name or '',
                'company': line.company_id.name or '',
            })
        return rows

    def _get_filter_label_block(self, filter_context):
        filter_labels = []

        if filter_context['organization_ids']:
            names = request.env['hr.organization'].browse(filter_context['organization_ids']).mapped('name')
            if names:
                filter_labels.append("Organizations: %s" % ", ".join(names))

        if filter_context['project_ids']:
            names = request.env['project.project'].browse(filter_context['project_ids']).mapped('name')
            if names:
                filter_labels.append("Projects: %s" % ", ".join(names))

        if filter_context['task_ids']:
            names = request.env['project.task'].browse(filter_context['task_ids']).mapped('name')
            if names:
                filter_labels.append("Tasks: %s" % ", ".join(names))

        if filter_context['employee_ids']:
            names = request.env['hr.employee'].browse(filter_context['employee_ids']).mapped('name')
            if names:
                filter_labels.append("Employees: %s" % ", ".join(names))

        if filter_context['selected_year']:
            filter_labels.append("Year: %s" % filter_context['selected_year'])

        if filter_context['selected_month']:
            filter_labels.append(
                "Month: %s" % self.MONTH_LABELS.get(filter_context['selected_month'], filter_context['selected_month'])
            )

        if filter_context['date_from'] or filter_context['date_to']:
            from_label = fields.Date.to_string(filter_context['date_from']) if filter_context['date_from'] else 'Any'
            to_label = fields.Date.to_string(filter_context['date_to']) if filter_context['date_to'] else 'Any'
            filter_labels.append("Date Range: %s to %s" % (from_label, to_label))

        if not filter_labels:
            return "No filters applied"
        return " | ".join(filter_labels)

    def _build_chart_payload(self, analytic_line_model, full_domain):
        employee_hours_groups = analytic_line_model._read_group(
            domain=full_domain + [('employee_id', '!=', False)],
            groupby=['employee_id'],
            aggregates=['unit_amount:sum'],
        )
        employee_hours = []
        for group in employee_hours_groups:
            employee = group[0]
            hours = float(group[1] or 0.0)
            if employee and hours:
                employee_hours.append({
                    'employee_id': employee.id,
                    'employee_name': employee.name or 'Unknown Employee',
                    'hours': hours,
                })
        employee_hours.sort(key=lambda row: (-row['hours'], row['employee_name'].lower()))

        employee_hierarchy_groups = analytic_line_model._read_group(
            domain=full_domain + [('employee_id', '!=', False)],
            groupby=['employee_id', 'date:month', 'project_id', 'task_id'],
            aggregates=['unit_amount:sum'],
        )
        hours_per_employee_hierarchy = []
        for group in employee_hierarchy_groups:
            employee = group[0]
            date_month = group[1]
            project = group[2]
            task = group[3]
            hours = float(group[4] or 0.0)
            if not employee or not hours:
                continue
            hours_per_employee_hierarchy.append({
                'employee_id': employee.id,
                'employee_name': employee.name or 'Unknown Employee',
                'date:month': date_month,
                'project_id': project.id if project else False,
                'project_name': project.name or '' if project else '',
                'task_id': task.id if task else False,
                'task_name': task.name or '' if task else '',
                'hours': hours,
            })
        hours_per_employee_hierarchy.sort(
            key=lambda r: (-r['hours'], (r['employee_name'] or '').lower())
        )

        hours_over_time_groups = analytic_line_model._read_group(
            domain=full_domain,
            groupby=['date:day'],
            aggregates=['unit_amount:sum'],
        )
        hours_over_time = []
        for group in hours_over_time_groups:
            day_value = self._extract_date_value(group[0])
            if day_value:
                hours_over_time.append({
                    'date': fields.Date.to_string(day_value),
                    'hours': float(group[1] or 0.0),
                })
        hours_over_time.sort(key=lambda row: row['date'])

        project_hours_groups = analytic_line_model._read_group(
            domain=full_domain + [('project_id', '!=', False)],
            groupby=['project_id'],
            aggregates=['unit_amount:sum'],
        )
        project_hours = []
        for group in project_hours_groups:
            project = group[0]
            hours = float(group[1] or 0.0)
            if project and hours:
                project_hours.append({
                    'project_id': project.id,
                    'project_name': project.name or 'Unnamed Project',
                    'hours': hours,
                })
        project_hours.sort(key=lambda row: (-row['hours'], row['project_name'].lower()))

        project_hierarchy_groups = analytic_line_model._read_group(
            domain=full_domain + [('project_id', '!=', False)],
            groupby=['project_id', 'task_id', 'employee_id'],
            aggregates=['unit_amount:sum'],
        )
        hours_per_project_hierarchy = []
        for group in project_hierarchy_groups:
            project = group[0]
            task = group[1]
            employee = group[2]
            hours = float(group[3] or 0.0)
            if not project or not hours:
                continue
            hours_per_project_hierarchy.append({
                'project_id': project.id,
                'project_name': project.name or 'Unnamed Project',
                'task_id': task.id if task else False,
                'task_name': task.name or '' if task else '',
                'employee_id': employee.id if employee else False,
                'employee_name': employee.name or '' if employee else '',
                'hours': hours,
            })
        hours_per_project_hierarchy.sort(
            key=lambda r: (-r['hours'], (r['project_name'] or '').lower(), (r['task_name'] or '').lower(), (r['employee_name'] or '').lower())
        )

        organization_hours_groups = analytic_line_model._read_group(
            domain=full_domain + [('organization_id', '!=', False)],
            groupby=['organization_id'],
            aggregates=['unit_amount:sum'],
        )
        organization_hours = []
        for group in organization_hours_groups:
            organization = group[0]
            hours = float(group[1] or 0.0)
            if organization and hours:
                organization_hours.append({
                    'organization_id': organization.id,
                    'organization_name': organization.name or 'Unnamed Organization',
                    'hours': hours,
                })
        organization_hours.sort(key=lambda row: (-row['hours'], row['organization_name'].lower()))

        employees_per_company_groups = analytic_line_model._read_group(
            domain=full_domain + [('organization_id', '!=', False), ('employee_id', '!=', False)],
            groupby=['organization_id', 'employee_id'],
            aggregates=['id:count'],
        )
        org_employee_count = {}
        org_names = {}
        for group in employees_per_company_groups:
            organization = group[0]
            employee = group[1]
            if not organization or not employee:
                continue
            oid = organization.id
            org_names[oid] = organization.name or 'Unnamed'
            org_employee_count[oid] = org_employee_count.get(oid, 0) + 1
        employees_per_company = [
            {'organization_id': oid, 'organization_name': org_names.get(oid, 'Unnamed'), 'employees_count': cnt}
            for oid, cnt in sorted(org_employee_count.items(), key=lambda x: (-x[1], (org_names.get(x[0], '')).lower()))
        ]

        employee_task_groups = analytic_line_model._read_group(
            domain=full_domain + [('employee_id', '!=', False), ('task_id', '!=', False)],
            groupby=['employee_id', 'task_id'],
            aggregates=['unit_amount:sum'],
        )
        employee_task_map = {}
        for group in employee_task_groups:
            employee = group[0]
            task = group[1]
            hours = float(group[2] or 0.0)
            if not employee or not task or not hours:
                continue
            key = str(employee.id)
            bucket = employee_task_map.setdefault(key, {
                'employee_id': employee.id,
                'employee_name': employee.name or 'Unknown Employee',
                'tasks': [],
            })
            bucket['tasks'].append({
                'task_id': task.id,
                'task_name': task.name or 'Unnamed Task',
                'hours': hours,
            })
        for bucket in employee_task_map.values():
            bucket['tasks'].sort(key=lambda row: (-row['hours'], row['task_name'].lower()))

        project_task_groups = analytic_line_model._read_group(
            domain=full_domain + [('project_id', '!=', False), ('task_id', '!=', False)],
            groupby=['project_id', 'task_id'],
            aggregates=['unit_amount:sum'],
        )
        project_task_map = {}
        for group in project_task_groups:
            project = group[0]
            task = group[1]
            hours = float(group[2] or 0.0)
            if not project or not task or not hours:
                continue
            key = str(project.id)
            bucket = project_task_map.setdefault(key, {
                'project_id': project.id,
                'project_name': project.name or 'Unnamed Project',
                'tasks': [],
            })
            bucket['tasks'].append({
                'task_id': task.id,
                'task_name': task.name or 'Unnamed Task',
                'hours': hours,
            })
        for bucket in project_task_map.values():
            bucket['tasks'].sort(key=lambda row: (-row['hours'], row['task_name'].lower()))

        day_employee_groups = analytic_line_model._read_group(
            domain=full_domain + [('employee_id', '!=', False)],
            groupby=['date:day', 'employee_id'],
            aggregates=['unit_amount:sum'],
        )
        day_project_groups = analytic_line_model._read_group(
            domain=full_domain + [('project_id', '!=', False)],
            groupby=['date:day', 'project_id'],
            aggregates=['unit_amount:sum'],
        )
        day_task_groups = analytic_line_model._read_group(
            domain=full_domain + [('task_id', '!=', False)],
            groupby=['date:day', 'task_id'],
            aggregates=['unit_amount:sum'],
        )
        day_breakdown = {}
        for row in hours_over_time:
            day_breakdown[row['date']] = {
                'date': row['date'],
                'total_hours': row['hours'],
                'employees': [],
                'projects': [],
                'tasks': [],
            }

        for group in day_employee_groups:
            day_value = self._extract_date_value(group[0])
            employee = group[1]
            hours = float(group[2] or 0.0)
            if not day_value or not employee or not hours:
                continue
            day_key = fields.Date.to_string(day_value)
            bucket = day_breakdown.setdefault(day_key, {
                'date': day_key,
                'total_hours': 0.0,
                'employees': [],
                'projects': [],
                'tasks': [],
            })
            bucket['employees'].append({
                'employee_id': employee.id,
                'employee_name': employee.name or 'Unknown Employee',
                'hours': hours,
            })

        for group in day_project_groups:
            day_value = self._extract_date_value(group[0])
            project = group[1]
            hours = float(group[2] or 0.0)
            if not day_value or not project or not hours:
                continue
            day_key = fields.Date.to_string(day_value)
            bucket = day_breakdown.setdefault(day_key, {
                'date': day_key,
                'total_hours': 0.0,
                'employees': [],
                'projects': [],
                'tasks': [],
            })
            bucket['projects'].append({
                'project_id': project.id,
                'project_name': project.name or 'Unnamed Project',
                'hours': hours,
            })

        for group in day_task_groups:
            day_value = self._extract_date_value(group[0])
            task = group[1]
            hours = float(group[2] or 0.0)
            if not day_value or not task or not hours:
                continue
            day_key = fields.Date.to_string(day_value)
            bucket = day_breakdown.setdefault(day_key, {
                'date': day_key,
                'total_hours': 0.0,
                'employees': [],
                'projects': [],
                'tasks': [],
            })
            bucket['tasks'].append({
                'task_id': task.id,
                'task_name': task.name or 'Unnamed Task',
                'hours': hours,
            })

        for details in day_breakdown.values():
            details['employees'].sort(key=lambda row: (-row['hours'], row['employee_name'].lower()))
            details['projects'].sort(key=lambda row: (-row['hours'], row['project_name'].lower()))
            details['tasks'].sort(key=lambda row: (-row['hours'], row['task_name'].lower()))

        return {
            'hours_per_employee': employee_hours,
            'hours_per_employee_hierarchy': hours_per_employee_hierarchy,
            'hours_over_time': hours_over_time,
            'hours_per_project': project_hours,
            'hours_per_project_hierarchy': hours_per_project_hierarchy,
            'hours_per_organization': organization_hours,
            'employees_per_company': employees_per_company,
            'employee_task_breakdown': employee_task_map,
            'project_task_breakdown': project_task_map,
            'day_breakdown': day_breakdown,
        }

    @route('/get/project/data', auth='user', type='json')
    def fetch_project_data(self, project_id=False, task_id=False, employee_id=False, organization_id=False, year=False, month=False, date_from=False, date_to=False):
        filter_context = self._build_filter_context(
            project_id=project_id,
            task_id=task_id,
            employee_id=employee_id,
            organization_id=organization_id,
            year=year,
            month=month,
            date_from=date_from,
            date_to=date_to,
        )

        analytic_line_model = request.env['account.analytic.line']
        timesheets = analytic_line_model.search(filter_context['full_domain'], order='date desc, id desc')

        project_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['task_domain']
            + filter_context['employee_domain']
            + filter_context['organization_domain']
            + filter_context['date_domain']
        )
        task_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['project_domain']
            + filter_context['employee_domain']
            + filter_context['organization_domain']
            + filter_context['date_domain']
        )
        employee_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['project_domain']
            + filter_context['task_domain']
            + filter_context['organization_domain']
            + filter_context['date_domain']
        )
        organization_options_domain = (
            list(filter_context['domain_core_date'])
            + filter_context['project_domain']
            + filter_context['task_domain']
            + filter_context['employee_domain']
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
        employees = [
            group[0] for group in analytic_line_model._read_group(
                domain=employee_options_domain,
                groupby=['employee_id'],
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
                'partner_id': project.partner_id.id if project.partner_id else False,
                'partner_name': project.partner_id.name if project.partner_id else '',
            }
            for project in sorted(projects, key=lambda item: (item.name or '').lower())
        ]

        tasks_data = [
            {
                'id': task.id,
                'name': task.name,
                'project_id': task.project_id.id if task.project_id else False,
                'project_name': task.project_id.name if task.project_id else '',
            }
            for task in sorted(tasks, key=lambda item: (item.name or '').lower())
        ]

        employees_data = [
            {
                'id': employee.id,
                'name': employee.name,
            }
            for employee in sorted(employees, key=lambda item: (item.name or '').lower())
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
        filtered_employees = timesheets.mapped('employee_id').filtered(lambda record: record.id)
        filtered_organizations = timesheets.mapped('organization_id').filtered(lambda record: record.id)
        total_hours = sum(timesheets.mapped('unit_amount')) if timesheets else 0.0
        chart_payload = self._build_chart_payload(analytic_line_model, filter_context['full_domain'])
        timesheet_rows = self._serialize_timesheet_rows(timesheets)

        if not timesheets:
            _logger.info('Timesheet Dashboard: No timesheets found for active filter combination')

        return {
            'projects_count': len(filtered_projects),
            'tasks_count': len(filtered_tasks),
            'employees_count': len(filtered_employees),
            'organizations_count': len(filtered_organizations),
            'timesheets_count': len(timesheets),
            'total_hours': total_hours,
            'projects': projects_data,
            'tasks': tasks_data,
            'employees': employees_data,
            'projects_ids': [project['id'] for project in projects_data],
            'tasks_ids': [task['id'] for task in tasks_data],
            'employees_ids': [employee['id'] for employee in employees_data],
            'organizations': organizations_data,
            'available_years': filter_context['available_years'],
            'available_months': filter_context['available_months'],
            'available_date_min': filter_context['available_date_min'],
            'available_date_max': filter_context['available_date_max'],
            'charts': chart_payload,
            'timesheet_rows': timesheet_rows,
        }

    @route('/timesheet_analytics/export/xlsx', type='http', auth='user')
    def export_timesheet_xlsx(self, data=None, **kw):
        if not xlsxwriter:
            return request.not_found()

        params = {}
        if data:
            try:
                params = json.load(data) if isinstance(data, FileStorage) else json.loads(data)
            except Exception:
                _logger.exception("Timesheet export: invalid payload received")
                params = {}

        filter_context = self._build_filter_context(
            project_id=params.get('project_id'),
            task_id=params.get('task_id'),
            employee_id=params.get('employee_id'),
            organization_id=params.get('organization_id'),
            year=params.get('year'),
            month=params.get('month'),
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
        )
        selected_columns = self._normalize_export_columns(params.get('columns'))
        analytic_line_model = request.env['account.analytic.line']
        timesheets = analytic_line_model.search(filter_context['full_domain'], order='date asc, id asc')

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Timesheets')

        title_style = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'font_color': '#1F2937',
            'align': 'left',
            'valign': 'vcenter',
        })
        meta_style = workbook.add_format({
            'font_size': 10,
            'font_color': '#475569',
            'text_wrap': True,
        })
        filter_style = workbook.add_format({
            'font_size': 10,
            'font_color': '#1E293B',
            'bg_color': '#EEF2FF',
            'border': 1,
            'border_color': '#C7D2FE',
            'text_wrap': True,
            'valign': 'top',
        })
        header_style = workbook.add_format({
            'bold': True,
            'font_color': '#FFFFFF',
            'bg_color': '#4F46E5',
            'border': 1,
            'border_color': '#4338CA',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
        })

        cell_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'text_wrap': True,
            'valign': 'top',
        })
        cell_alt_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'bg_color': '#F8FAFC',
            'text_wrap': True,
            'valign': 'top',
        })

        date_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'num_format': 'yyyy-mm-dd',
            'text_wrap': True,
            'valign': 'top',
        })
        date_alt_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'bg_color': '#F8FAFC',
            'num_format': 'yyyy-mm-dd',
            'text_wrap': True,
            'valign': 'top',
        })

        hours_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'num_format': '#,##0.00',
            'text_wrap': True,
            'align': 'right',
            'valign': 'top',
        })
        hours_alt_style = workbook.add_format({
            'border': 1,
            'border_color': '#E2E8F0',
            'bg_color': '#F8FAFC',
            'num_format': '#,##0.00',
            'text_wrap': True,
            'align': 'right',
            'valign': 'top',
        })

        no_data_style = workbook.add_format({
            'italic': True,
            'font_color': '#64748B',
            'border': 1,
            'border_color': '#E2E8F0',
            'text_wrap': True,
            'valign': 'top',
        })

        for column_index, column_key in enumerate(selected_columns):
            column_width = self.EXPORT_COLUMN_DEFINITIONS[column_key]['width']
            worksheet.set_column(column_index, column_index, column_width)

        worksheet.set_default_row(24)

        company = request.env.company
        title_col_start = 0
        if company.logo:
            try:
                logo_bytes = io.BytesIO(base64.b64decode(company.logo))
                worksheet.set_row(0, 64)
                worksheet.insert_image(
                    0,
                    0,
                    'company_logo.png',
                    {
                        'image_data': logo_bytes,
                        'x_scale': 0.5,
                        'y_scale': 0.5,
                        'x_offset': 2,
                        'y_offset': 2,
                    },
                )
                title_col_start = 2
            except Exception:
                _logger.exception("Timesheet export: unable to render company logo for company %s", company.id)

        title_end_col = max(len(selected_columns) - 1, title_col_start + 3)
        worksheet.merge_range(0, title_col_start, 0, title_end_col, 'Timesheet Export', title_style)

        generated_at = fields.Datetime.now()
        generated_local = fields.Datetime.context_timestamp(request.env.user, generated_at)
        generated_label = generated_local.strftime('%Y-%m-%d %H:%M:%S')
        worksheet.merge_range(
            1,
            title_col_start,
            1,
            title_end_col,
            "Company: %s | Generated: %s" % (company.display_name, generated_label),
            meta_style,
        )

        filter_label_block = self._get_filter_label_block(filter_context)
        worksheet.merge_range(2, 0, 2, title_end_col, "Applied Filters: %s" % filter_label_block, filter_style)
        worksheet.set_row(2, 38)

        table_header_row = 4
        for column_index, column_key in enumerate(selected_columns):
            worksheet.write(
                table_header_row,
                column_index,
                self.EXPORT_COLUMN_DEFINITIONS[column_key]['label'],
                header_style,
            )

        data_row_start = table_header_row + 1
        if timesheets:
            for row_offset, line in enumerate(timesheets):
                row = data_row_start + row_offset
                use_alternate = bool(row_offset % 2)

                for column_index, column_key in enumerate(selected_columns):
                    value = self._get_column_value(line, column_key)

                    if column_key == 'date':
                        style = date_alt_style if use_alternate else date_style
                    elif column_key == 'hours':
                        style = hours_alt_style if use_alternate else hours_style
                    else:
                        style = cell_alt_style if use_alternate else cell_style
                        if value in (False, None):
                            value = ''

                    worksheet.write(row, column_index, value, style)

            data_row_end = data_row_start + len(timesheets) - 1
            worksheet.autofilter(table_header_row, 0, data_row_end, len(selected_columns) - 1)
        else:
            worksheet.merge_range(
                data_row_start,
                0,
                data_row_start,
                max(0, len(selected_columns) - 1),
                'No timesheet entries found for the applied filters.',
                no_data_style,
            )

        worksheet.freeze_panes(data_row_start, 0)
        workbook.close()

        xlsx_data = output.getvalue()
        filename = osutil.clean_filename("Timesheet Export %s" % fields.Date.today())
        return request.make_response(
            xlsx_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition('%s.xlsx' % filename)),
            ],
        )

    @route('/timesheet_analytics/export/pivot/presets/xlsx', type='http', auth='user')
    def export_timesheet_pivot_presets_xlsx(self, data=None, **kw):
        if not xlsxwriter:
            return request.not_found()

        params = {}
        if data:
            try:
                params = json.load(data) if isinstance(data, FileStorage) else json.loads(data)
            except Exception:
                _logger.exception("Timesheet pivot export: invalid payload received")
                params = {}

        filter_context = self._build_filter_context(
            project_id=params.get('project_id'),
            task_id=params.get('task_id'),
            employee_id=params.get('employee_id'),
            organization_id=params.get('organization_id'),
            year=params.get('year'),
            month=params.get('month'),
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
        )
        preset_keys = params.get('pivot_presets') or []
        if not isinstance(preset_keys, (list, tuple)):
            preset_keys = []

        xlsx_data = self._export_pivot_presets_xlsx(filter_context, preset_keys)
        filename = osutil.clean_filename("Timesheet Pivot Export %s" % fields.Date.today())
        return request.make_response(
            xlsx_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition('%s.xlsx' % filename)),
            ],
        )

