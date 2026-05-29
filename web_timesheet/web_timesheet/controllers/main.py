import math
import base64
import xlrd
import json
import re
from collections import OrderedDict
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from odoo import fields, http, _
from odoo.http import request
from datetime import datetime
from odoo.tools import date_utils, groupby as groupbyelem
from odoo.tools import float_round
from odoo.exceptions import ValidationError
from odoo.osv.expression import AND
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal

regex_patterns = {
    '%d/%m/%Y': r'^\d{1,2}/\d{1,2}/\d{4}$',  # 5/6/2024
    '%d-%B-%y': r'^\d{1,2}-[A-Za-z]+-\d{2}$',  # 5-June-24
    '%d-%m-%y': r'^\d{1,2}-\d{1,2}-\d{2}$',  # 5-6-24
    '%d/%m/%y': r'^\d{1,2}/\d{1,2}/\d{2}$',  # 5/6/24
    '%d-%m-%Y': r'^\d{1,2}-\d{1,2}-\d{4}$',  # 5-6-2024
    '%Y-%m-%d': r'^\d{4}-\d{2}-\d{2}$',  # 2024-12-31
}
other_date_formats = ["%d %b %Y", "%d %B %Y"]


class TimesheetCustomerPortal(TimesheetCustomerPortal):
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='none',
                             **kw):
        Timesheet = request.env['account.analytic.line']
        domain = Timesheet._timesheet_get_portal_domain()
        if request.env.user.has_group('base.group_user'):
            domain += ([('user_id', '=', request.env.user.id)])
        else:
            domain = ([('portal_user_id', '=', request.env.user.id)])
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
                    raw_timesheets_group = Timesheet_sudo.read_group(
                        domain, ["unit_amount:sum", "ids:array_agg(id)"], ["date:day"]
                    )
                    grouped_timesheets = [(Timesheet_sudo.browse(group["ids"]), group["unit_amount"]) for group in
                                          raw_timesheets_group]

                else:
                    time_data = Timesheet_sudo.read_group(domain, [field, 'unit_amount:sum'], [field])
                    mapped_time = dict([(m[field][0] if m[field] else False, m['unit_amount']) for m in time_data])
                    grouped_timesheets = [(Timesheet_sudo.concat(*g), mapped_time[k.id]) for k, g in
                                          groupbyelem(timesheets, itemgetter(field))]
                return timesheets, grouped_timesheets

            grouped_timesheets = [(
                timesheets,
                sum(Timesheet_sudo.search(domain).mapped('unit_amount'))
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


def time_to_float(hour, minute):
    return float_round(hour + minute / 60, precision_digits=2)


class WebsiteTimesheet(http.Controller):

    @http.route(['/get_task_data'], type='http', csrf=False, methods=['post'], auth="public", website=True)
    def get_task_data(self, **post):
        if post.get('search') and len(post.get('search')) > 0:
            search_string = post.get('search').split('-')[0]
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
            task_id = request.env['project.task'].sudo().search([('id', '=', int(kw.get('ts_task_id')))])
            print(kw.get('task'))

        else:

            error = 'Invalid Task Selection ' + (
                                                               'Please contact the Project '
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
                                                               'database if you cannot find the task on the dropdown list')
            raise ValidationError(_(error))

        company = False
        if kw.get('company_id'):
            company = request.env['res.company'].sudo().search([('id', '=', int(kw.get('company_id')))])
        else:
            company = request.env.user.company_id


        try:
            fractional, time = math.modf(float(kw.get('duration').replace(":", ".")))
            float_time = time_to_float(time, int(float_round(fractional, 2) * (10 ** 2)))
            vals = {
                'company_id': company.id if company else request.env.user.company_id.id,
                'employee_id': int(kw.get('employee_id')) if kw.get('employee_id') else False,
                'project_id': project_id.id if project_id else task_id.project_id.id,
                'task_id': task_id.id if task_id else False,
                'date': kw.get('date'),
                # 'date': formatted_date if 'formatted_date' in locals() else False,
                'unit_amount': float_time,
                'name': kw.get('description'),
                'portal_user_id': request.env.user.id,
                'ts_company_id': kw.get('ts_company_id'),
                'expenditure_type': kw.get('expenditure_type'),

            }
            request.env['account.analytic.line'].sudo().create(vals)
            return request.redirect('/my/timesheets')
        except:
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
            fractional, time = math.modf(float(kw.get('duration').replace(":", ".")))
            float_time = time_to_float(time, int(float_round(fractional, 2) * (10 ** 2)))
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
                        date_string = row[3].value
                        if date_string:
                            for fmt, pattern in regex_patterns.items():
                                if re.match(pattern, date_string):
                                    date_object = datetime.strptime(date_string, fmt).date()
                                    date = date_object.strftime('%Y-%m-%d')
                                else:
                                    try:
                                        if type(self.convert_to_date(date_string)) != str:
                                            date_object = self.convert_to_date(date_string).date()
                                            date = date_object.strftime('%Y-%m-%d')
                                        else:
                                            date_fmt = "%d %B %Y"
                                            date_object = datetime.strptime(date_string, date_fmt)
                                            date = date_object.strftime('%Y-%m-%d')

                                    except ValueError as e:

                                        error = ('Invalid Date format :- %s' % (date_string))
                        else:
                            date = datetime.today()

                        expenditure_type = row[4].value
                        hours = row[5].value
                        description = row[6].value

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
                                'name': description,
                                'project_id': project.id,
                                'task_id': task.id if task else False,
                            })

                return request.redirect('/my/timesheets')
        except:

            if error:

                raise ValidationError(_(error))

            else:

                raise ValidationError(_('Timesheet is not Imported.'))



    def convert_to_date(self, date_str):
        for fmt in other_date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                return date_str

