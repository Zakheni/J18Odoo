import json
import re
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta

try:
    import xlrd
except ImportError:
    xlrd = None

from odoo import fields, http, _
from odoo.http import request
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.tools import float_round
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND, OR
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.hr_timesheet.controllers.portal import (
    TimesheetCustomerPortal as HrTimesheetCustomerPortal,
)

INVALID_TASK_SELECTION_MSG = (
    'Invalid Task Selection Please contact the Project '
    'Management Team: \n\n '
    'Murendwa - murendwar@zakhenict.co.za '
    '\n Patricia - patriciam@zakhenict.co.za '
    '\n Dennis - dennisk@zakhenict.co.za '
    '\n Zikhona - zikhonan@zakhenict.co.za '
    '\n and Thando - thandom@zakhenict.co.za '
    '\n\nto assist with registering the task into the '
    'database if you cannot find the task on the dropdown list'
)

EXCEL_TEXT_DATE_FORMATS = [
    '%Y-%m-%d',
    '%Y/%m/%d',
    '%Y.%m.%d',
    '%Y%m%d',
    '%d/%m/%Y',
    '%d-%m-%Y',
    '%d.%m.%Y',
    '%m/%d/%Y',
    '%m-%d-%Y',
    '%m.%d.%Y',
    '%d/%m/%y',
    '%d-%m-%y',
    '%d.%m.%y',
    '%m/%d/%y',
    '%m-%d-%y',
    '%m.%d.%y',
    '%d %b %Y',
    '%d %B %Y',
    '%b %d %Y',
    '%B %d %Y',
    '%d %b %y',
    '%d %B %y',
    '%b %d %y',
    '%B %d %y',
    '%d-%b-%Y',
    '%d-%B-%Y',
    '%b-%d-%Y',
    '%B-%d-%Y',
    '%d-%b-%y',
    '%d-%B-%y',
    '%b-%d-%y',
    '%B-%d-%y',
    '%d/%b/%Y',
    '%d/%B/%Y',
    '%d/%b/%y',
    '%d/%B/%y',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d %H:%M',
    '%d/%m/%Y %H:%M:%S',
    '%d/%m/%Y %H:%M',
    '%m/%d/%Y %H:%M:%S',
    '%m/%d/%Y %H:%M',
]


class TimesheetCustomerPortal(HrTimesheetCustomerPortal):
    def _get_current_user_employee_ids(self):
        user = request.env.user
        return request.env['hr.employee'].sudo().search([
            '|',
            ('user_id', '=', user.id),
            ('work_contact_id', '=', user.partner_id.id),
        ]).ids

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none',
                             **kw):
        Timesheet = request.env['account.analytic.line']
        base_domain = Timesheet._timesheet_get_portal_domain()
        employee_ids = self._get_current_user_employee_ids()
        user_domain = [('user_id', '=', request.env.user.id)]
        employee_domain = [('employee_id', 'in', employee_ids)] if employee_ids else []

        if request.env.user.has_group('base.group_user'):
            if employee_domain:
                domain = AND([base_domain, OR([user_domain, employee_domain])])
            else:
                domain = AND([base_domain, user_domain])
        else:
            # Portal-only users: model domain already includes employee and portal_user_id OR branches.
            domain = base_domain
        Timesheet_sudo = Timesheet.sudo()
        values = self._prepare_portal_layout_values()
        _items_per_page = 100

        searchbar_sortings = self._get_searchbar_sortings()

        searchbar_inputs = self._get_searchbar_inputs()

        searchbar_groupby = self._get_searchbar_groupby()

        today = fields.Date.today()
        quarter_start, quarter_end = date_utils.get_quarter(today)
        last_week = today + relativedelta(weeks=-1)
        last_month = today + relativedelta(months=-1)
        last_year = today + relativedelta(years=-1)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'today': {'label': _('Today'), 'domain': [("date", "=", today)]},
            'week': {'label': _('This week'), 'domain': [('date', '>=', date_utils.start_of(today, "week")),
                                                         ('date', '<=', date_utils.end_of(today, 'week'))]},
            'month': {'label': _('This month'), 'domain': [('date', '>=', date_utils.start_of(today, 'month')),
                                                           ('date', '<=', date_utils.end_of(today, 'month'))]},
            'year': {'label': _('This year'), 'domain': [('date', '>=', date_utils.start_of(today, 'year')),
                                                         ('date', '<=', date_utils.end_of(today, 'year'))]},
            'quarter': {'label': _('This Quarter'),
                        'domain': [('date', '>=', quarter_start), ('date', '<=', quarter_end)]},
            'last_week': {'label': _('Last week'), 'domain': [('date', '>=', date_utils.start_of(last_week, "week")),
                                                              ('date', '<=', date_utils.end_of(last_week, 'week'))]},
            'last_month': {'label': _('Last month'),
                           'domain': [('date', '>=', date_utils.start_of(last_month, 'month')),
                                      ('date', '<=', date_utils.end_of(last_month, 'month'))]},
            'last_year': {'label': _('Last year'), 'domain': [('date', '>=', date_utils.start_of(last_year, 'year')),
                                                              ('date', '<=', date_utils.end_of(last_year, 'year'))]},
        }
        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = AND([domain, searchbar_filters[filterby]['domain']])

        if search and search_in:
            domain += self._get_search_domain(search_in, search)

        timesheet_count = Timesheet_sudo.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/timesheets",
            url_args={'sortby': sortby, 'search_in': search_in, 'search': search, 'filterby': filterby,
                      'groupby': groupby},
            total=timesheet_count,
            page=page,
            step=_items_per_page
        )

        def get_timesheets():
            groupby_mapping = self._get_groupby_mapping()
            field = groupby_mapping.get(groupby, None)
            orderby = '%s, %s' % (field, order) if field else order
            timesheets = Timesheet_sudo.search(domain, order=orderby, limit=_items_per_page, offset=pager['offset'])
            if field:
                if groupby == 'date':
                    raw_timesheets_group = Timesheet_sudo._read_group(
                        domain, ['date:day'], ['unit_amount:sum', 'id:recordset']
                    )
                    grouped_timesheets = [(records, unit_amount) for __, unit_amount, records in raw_timesheets_group]

                else:
                    time_data = Timesheet_sudo._read_group(domain, [field], ['unit_amount:sum'])
                    mapped_time = {group_key.id: unit_amount for group_key, unit_amount in time_data}
                    grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g in
                                          groupbyelem(timesheets, itemgetter(field))]
                return timesheets, grouped_timesheets

            grouped_timesheets = [(
                timesheets,
                Timesheet_sudo._read_group(domain, aggregates=['unit_amount:sum'])[0][0]
            )] if timesheets else []
            return timesheets, grouped_timesheets

        timesheets, grouped_timesheets = get_timesheets()
        values.update({
            'timesheets': timesheets,
            'grouped_timesheets': grouped_timesheets,
            'page_name': 'timesheet',
            'default_url': '/my/timesheets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'is_uom_day': request.env['account.analytic.line']._is_timesheet_encode_uom_day(),
        })
        return request.render("hr_timesheet.portal_my_timesheets", values)


def parse_duration_hours(raw):
    """Interpret portal duration as decimal hours, or 'H:MM' / 'H:M' as hours and minutes."""
    if raw is None:
        return 0.0
    if isinstance(raw, (int, float)):
        return float_round(float(raw), precision_digits=2)
    s = str(raw).strip().replace(',', '.')
    if not s:
        return 0.0
    if ':' in s:
        parts = s.split(':', 1)
        try:
            h = float(parts[0] or 0)
        except ValueError:
            h = 0.0
        try:
            m = float((parts[1] or '').strip() or 0)
        except ValueError:
            m = 0.0
        return float_round(h + m / 60.0, precision_digits=2)
    try:
        return float_round(float(s), precision_digits=2)
    except ValueError:
        return 0.0


def portal_timesheet_description_text(raw):
    """Normalize description from form or spreadsheet cell."""
    if raw is None or raw is False:
        return ''
    if isinstance(raw, str):
        return raw.strip()
    if isinstance(raw, float) and raw == int(raw):
        return str(int(raw))
    return str(raw).strip()


def portal_timesheet_assure_description(raw, sheet_name=None, row_number=None):
    text = portal_timesheet_description_text(raw)
    if text:
        return text
    if sheet_name is not None and row_number is not None:
        raise ValidationError(
            _(
                'The description cannot be empty. Each imported line must include a description '
                '(Sheet: %(sheet)s, Row: %(row)s).'
            )
            % {'sheet': sheet_name, 'row': row_number}
        )
    raise ValidationError(
        _('The description cannot be empty. Please enter a description for the timesheet.')
    )


def portal_timesheet_assure_not_future_date(env, date_str, sheet_name=None, row_number=None):
    if not date_str:
        if sheet_name is not None and row_number is not None:
            raise ValidationError(
                _('A date is required for each imported line (Sheet: %(sheet)s, Row: %(row)s).')
                % {'sheet': sheet_name, 'row': row_number}
            )
        raise ValidationError(_('Please select a date for the timesheet.'))
    try:
        line_date = fields.Date.from_string(date_str)
    except ValueError:
        if sheet_name is not None and row_number is not None:
            raise ValidationError(
                _('The date is not valid (Sheet: %(sheet)s, Row: %(row)s).')
                % {'sheet': sheet_name, 'row': row_number}
            )
        raise ValidationError(_('The date is not valid. Please select a valid date.'))
    today = fields.Date.context_today(env['res.users'].browse(env.uid))
    if line_date > today:
        today_s = fields.Date.to_string(today)
        if sheet_name is not None and row_number is not None:
            raise ValidationError(
                _(
                    'Timesheets cannot be saved for a future date. The line date %(line)s is after '
                    'today (%(today)s). That row was not imported (Sheet: %(sheet)s, Row: %(row)s).'
                )
                % {
                    'line': date_str,
                    'today': today_s,
                    'sheet': sheet_name,
                    'row': row_number,
                }
            )
        raise ValidationError(
            _(
                'Timesheets cannot be saved for a future date. The selected date %(line)s is after '
                'today (%(today)s). Please choose today or an earlier date.'
            )
            % {'line': date_str, 'today': today_s}
        )


class WebsiteTimesheet(http.Controller):

    def _ensure_xlrd_available(self):
        if xlrd is not None:
            return
        raise ValidationError(
            _(
                'The Python library "xlrd" is required to import timesheets. '
                'Install it in your Odoo environment and try again.'
            )
        )

    @http.route(['/get_task_data'], type='http', csrf=False, methods=['post'], auth="public", website=True)
    def get_task_data(self, **post):
        if post.get('search') and len(post.get('search')) > 0:
            project = post.get('search').split('-')[1]
            task_list = request.env['project.task'].sudo().search_read(
                [('project_id', '=', int(project))],
                ['id', 'name'])
            result = json.dumps([{'value': each['name'],
                                  'id': each['id'],
                                  } for each in task_list])
        else:
            result = json.dumps([])
        return result

    @http.route(['/timesheet/form'], type='http', auth="user", website=True)
    def ts_create(self, **kw):
        project_id = False
        if kw.get('project'):
            project_id = request.env['project.project'].sudo().search([('id', '=', int(kw.get('project')))])
            if project_id:
                project_id.message_partner_ids = [request.env.user.partner_id.id]

        task_id = False
        if kw.get('ts_task_id'):
            task_id = request.env['project.task'].sudo().browse(int(kw.get('ts_task_id')))
            if not task_id.exists():
                raise ValidationError(_(INVALID_TASK_SELECTION_MSG))
            if project_id and task_id.project_id != project_id:
                raise ValidationError(_('The selected task does not belong to the selected project.'))

        else:
            raise ValidationError(_(INVALID_TASK_SELECTION_MSG))

        company = False
        if kw.get('company_id'):
            company = request.env['res.company'].sudo().search([('id', '=', int(kw.get('company_id')))])
        else:
            company = request.env.user.company_id


        try:
            portal_employee = request.env['hr.employee'].sudo().search(
                [
                    '|',
                    ('user_id', '=', request.env.user.id),
                    ('work_contact_id', '=', request.env.user.partner_id.id),
                ],
                limit=1,
            )
            employee_id = int(kw.get('employee_id')) if kw.get('employee_id') else False
            if not request.env.user.has_group('base.group_user'):
                employee_id = portal_employee.id if portal_employee else False
            else:
                employee_id = employee_id or (portal_employee.id if portal_employee else False)
            if not employee_id:
                raise ValidationError(_('No employee is linked to your user. Please contact an administrator.'))

            portal_timesheet_assure_not_future_date(request.env, kw.get('date'))
            description_text = portal_timesheet_assure_description(kw.get('description'))

            float_time = parse_duration_hours(kw.get('duration'))
            vals = {
                'company_id': company.id if company else request.env.user.company_id.id,
                'employee_id': employee_id,
                'project_id': project_id.id if project_id else task_id.project_id.id,
                'task_id': task_id.id if task_id else False,
                'date': kw.get('date'),
                'unit_amount': float_time,
                'name': description_text,
                'portal_user_id': request.env.user.id,
                'ts_company_id': kw.get('ts_company_id'),
                'expenditure_type': kw.get('expenditure_type'),

            }
            request.env['account.analytic.line'].sudo().create(vals)
            return request.redirect('/my/timesheets')
        except ValidationError:
            raise
        except Exception:
            raise ValidationError(_('Timesheet is not created.'))

    @http.route(['/timesheet/form/project'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def project_infos(self, **kw):
        project_id = request.env['project.project'].sudo().browse(int(kw.get('project_id')))
        ts_company_id = False
        if project_id:
            organisation = dict(request.env['project.project'].sudo()._fields['ts_company_id'].selection).get(
                project_id.ts_company_id)
            ts_company_id = organisation

        return {'ts_company_id': ts_company_id}

    @http.route(['/timesheet/form/tasks'], type='json', auth='user', website=True)
    def tasks_for_project(self, project_id=None, **kw):
        """Return tasks for the portal create form dropdown (filtered by project)."""
        try:
            pid = int(project_id if project_id is not None else kw.get('project_id') or 0)
        except (TypeError, ValueError):
            pid = 0
        if not pid:
            return {'tasks': []}
        tasks = request.env['project.task'].sudo().search_read(
            [('project_id', '=', pid)],
            ['id', 'name'],
            order='name',
        )
        return {'tasks': [{'id': t['id'], 'name': t['name']} for t in tasks]}

    @http.route(['/my/delete_timesheet'], type='json', auth="user", website=True)
    def ts_delete(self, **kw):
        request.env['account.analytic.line'].sudo().search([('id', '=', kw.get('timesheet_id'))]).unlink()
        return True

    @http.route(['/my/edit_timesheet'], type='json', auth="user", website=True)
    def ts_edit(self, **kw):
        lang_obj = request.env['res.lang']
        language = request.env.user.lang
        lang_ids = lang_obj.search([('code', '=', language)])
        date_format = _('%d/%m/%Y')
        for lang in lang_ids:
            date_format = lang.date_format
        t_date = datetime.strptime(kw.get('date'), date_format)
        timesheet_date = fields.Date.to_string(t_date)
        project_id = request.env['project.project'].search([('id', '=', kw.get('project_id'))])
        task_id = request.env['project.task'].sudo().search([('id', '=', int(kw.get('task_id')))])


        organisation = ''
        if kw.get('ts_company_id'):
            organisations = dict(request.env['project.project'].sudo()._fields['ts_company_id'].selection)
            for key, val in organisations.items():
                if val == kw.get('ts_company_id'):
                    organisation = key

        try:
            float_time = parse_duration_hours(kw.get('duration'))
            vals = {
                'date': timesheet_date,
                'unit_amount': float_time,
                'name': kw.get('description'),
                'project_id': project_id.id,
                'task_id': task_id.id,
                'ts_company_id': organisation,
                'expenditure_type': kw.get('expenditure_type')
            }
            request.env['account.analytic.line'].sudo().search([('id', '=', kw.get('id'))]).write(vals)
            return True
        except:
            raise ValidationError(_('Timesheet is not edited.'))

    @http.route(['/import/timesheet/form'], type='http', auth="user", website=True, csrf=False)
    def ts_import(self, ts_xls, **kw):
        self._ensure_xlrd_available()
        error = ''
        try:
            if ts_xls:
                file_content = ts_xls.read()
                workbook = xlrd.open_workbook(file_contents=file_content)
                timesheet_model = request.env['account.analytic.line']

                for sheet in workbook.sheets():
                    for row_index in range(1, sheet.nrows):

                        # Excel records
                        row = sheet.row(row_index)
                        employee_name = row[0].value
                        project_name = row[1].value
                        task_name = row[2].value
                        date_cell = row[3]
                        try:
                            date = self._normalize_excel_date(date_cell, workbook.datemode)
                        except ValidationError as exc:
                            error = '%s (Sheet: %s, Row: %s)' % (
                                exc.args[0],
                                sheet.name,
                                row_index + 1,
                            )
                            raise ValidationError(_(error))

                        expenditure_type = row[4].value
                        hours = row[5].value
                        description = row[6].value

                        portal_timesheet_assure_not_future_date(
                            request.env, date, sheet_name=sheet.name, row_number=row_index + 1
                        )
                        description_text = portal_timesheet_assure_description(
                            description, sheet_name=sheet.name, row_number=row_index + 1
                        )

                        # Check data existance

                        employee = request.env['hr.employee'].sudo().search([('name', '=', employee_name)], limit=1)
                        project = request.env['project.project'].sudo().search([('name', '=', project_name)],limit=1)
                        task = request.env['project.task'].sudo().search([('name', '=', task_name)], limit=1)

                        # raise Exceptions
                        if not employee:

                            error  = 'Invalid employee - %s' % employee_name

                            raise ValidationError(_(error))

                        if not project:

                            error = 'Invalid Project named \"%s\"' % project_name + (' doesn\'t exist. Please '
                                                                                         'contact the Project '
                                                                                         'Management Team: \n\n '
                                                                                         'Murendwa - '
                                                                                         'murendwar@zakhenict.co.za '
                                                                                         '\n Patricia - '
                                                                                         'patriciam@zakhenict.co.za '
                                                                                         '\n Dennis -  '
                                                                                         'dennisk@zakhenict.co.za '
                                                                                         '\n Zikhona - '
                                                                                         'zikhonan@zakhenict.co.za '
                                                                                         '\n and Thando - '
                                                                                         'thandom@zakhenict.co.za '
                                                                                         '\n\nto assist with '
                                                                                         'registering '
                                                                                         'the project into the '
                                                                                         'database')
                            raise ValidationError(_(error))

                        if not task:

                            error = 'Invalid Task named \"%s\"' % task_name + (' doesn\'t exist. Please '
                                                                                         'contact the Project '
                                                                                         'Management Team: \n\n '
                                                                                         'Murendwa - '
                                                                                         'murendwar@zakhenict.co.za '
                                                                                         '\n Patricia - '
                                                                                         'patriciam@zakhenict.co.za '
                                                                                         '\n Dennis -  '
                                                                                         'dennisk@zakhenict.co.za '
                                                                                         '\n Zikhona - '
                                                                                         'zikhonan@zakhenict.co.za '
                                                                                         '\n and Thando - '
                                                                                         'thandom@zakhenict.co.za '
                                                                                         '\n\nto assist with '
                                                                                         'registering '
                                                                                         'the task into the '
                                                                                         'database')
                            raise ValidationError(_(error))


                        if project_name:

                            project = request.env['project.project'].sudo().search([('name', '=', project_name)],
                                                                                   limit=1)
                            project.message_partner_ids = [request.env.user.partner_id.id]


                            if task_name:
                                task = request.env['project.task'].sudo().search([('name', '=', task_name)], limit=1)


                            if expenditure_type == 'Normal':
                                expenditure = 'normal'
                            elif expenditure_type == 'Overtime':
                                expenditure = 'overtime'
                            elif expenditure_type == 'Weekend overtime':
                                expenditure = 'weekend_overtime'
                            elif expenditure_type == 'Public Holiday overtime':
                                expenditure = 'public_holiday_overtime'
                            else:
                                expenditure = 'normal'

                            # Create the timesheet entry
                            timesheet_model.sudo().create({

                                'portal_user_id': request.env.user.id,
                                'employee_id': employee.id if employee else False,
                                'date': date,
                                'unit_amount': hours,
                                'expenditure_type': expenditure,
                                'name': description_text,
                                'project_id': project.id,
                                'task_id': task.id if task else False,
                            })

                return request.redirect('/my/timesheets')
        except ValidationError:
            raise
        except Exception:

            if error:

                raise ValidationError(_(error))

            else:

                raise ValidationError(_('Timesheet is not Imported.'))
    def _normalize_excel_date(self, cell, datemode):
        value = cell.value

        # Empty date falls back to today to preserve current behavior.
        if cell.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or value in (None, ''):
            return fields.Date.to_string(fields.Date.today())

        if isinstance(value, datetime):
            return fields.Date.to_string(value.date())

        if isinstance(value, (int, float)):
            try:
                excel_date = xlrd.xldate.xldate_as_datetime(value, datemode)
                return fields.Date.to_string(excel_date.date())
            except (TypeError, ValueError, xlrd.XLDateError):
                parsed_number = str(int(value)) if float(value).is_integer() else str(value)
                parsed_date = self._parse_date_string(parsed_number)
                if parsed_date:
                    return parsed_date
                raise ValidationError(_('Invalid Date format :- %s') % value)

        parsed_date = self._parse_date_string(str(value))
        if parsed_date:
            return parsed_date

        raise ValidationError(_('Invalid Date format :- %s') % value)

    def _parse_date_string(self, raw_value):
        clean_value = (raw_value or '').strip()
        clean_value = clean_value.lstrip("'").strip()
        clean_value = re.sub(r'\s+', ' ', clean_value)
        if not clean_value:
            return False

        # Policy: if date is ambiguous (e.g. 01/02/2024), interpret as DD/MM.
        ambiguous_as_day_first = self._parse_ambiguous_as_day_first(clean_value)
        if ambiguous_as_day_first:
            return ambiguous_as_day_first

        for fmt in EXCEL_TEXT_DATE_FORMATS:
            try:
                parsed = datetime.strptime(clean_value, fmt)
                return fields.Date.to_string(parsed.date())
            except ValueError:
                continue

        try:
            parsed = date_parser.parse(clean_value, dayfirst=True, fuzzy=False)
            return fields.Date.to_string(parsed.date())
        except (TypeError, ValueError, OverflowError):
            return False

    def _parse_ambiguous_as_day_first(self, value):
        """
        For ambiguous numeric day/month values (e.g. 01/02/2024), force DD/MM.
        """
        match = re.match(
            r"^(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{2}|\d{4})(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?$",
            value,
        )
        if not match:
            return False

        first = int(match.group(1))
        second = int(match.group(2))
        if not (first <= 12 and second <= 12 and first != second):
            return False

        # Convert using DD/MM for ambiguous numeric forms.
        has_seconds = len(re.findall(r":", value)) == 2
        has_time = ":" in value
        year_len = len(match.group(3))
        base_fmt = '%d/%m/%Y' if year_len == 4 else '%d/%m/%y'
        if has_time:
            base_fmt += ' %H:%M:%S' if has_seconds else ' %H:%M'

        normalized = re.sub(r"[.-]", "/", value)
        parsed = datetime.strptime(normalized, base_fmt)
        return fields.Date.to_string(parsed.date())
