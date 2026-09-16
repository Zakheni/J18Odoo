from datetime import datetime, timedelta
from datetime import time as dt_time

import pytz
from odoo import api, fields, models
from odoo.addons.resource.models.utils import float_to_time


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    work_arrangement = fields.Selection([
        ('office', 'Office'),
        ('hybrid', 'Hybrid'),
        ('remote', 'Remote'),
        ('field', 'Field / Off-site'),
    ], string="Work Arrangement", default='office',
        help="How this employee normally works: from the office, hybrid, fully "
             "remote, or in the field (client-facing).")
    default_work_location_id = fields.Many2one(
        'zakheni.work.location', string="Default Work Location",
        help="Fallback work location used when the work schedule line for a "
             "day has no explicit location.")

    def _get_tz(self):
        return super()._get_tz()

    def _get_hybrid_schedule(self, day):
        """Return the planned work schedule for *day* (a date) for this employee.

        :returns: dict with keys
            'check_in_utc', 'check_out_utc' (naive UTC datetimes, defaults to a
            9h window if the calendar has no explicit line that day),
            'work_location_id' (zakheni.work.location record) or False,
            'calendar_id', 'attendance_lines' (recordset of resource.calendar.attendance)
        """
        self.ensure_one()
        calendar = self.resource_calendar_id or self.company_id.resource_calendar_id
        if not calendar:
            return {}

        tz_name = self._get_tz() or 'UTC'
        tz = pytz.timezone(tz_name)

        day_date = day
        day_local = tz.localize(datetime.combine(day_date, dt_time.min))

        this_week_type = self.env['resource.calendar.attendance'].get_week_type(day_date)
        week_type = str(this_week_type)

        lines = self.env['resource.calendar.attendance'].search([
            ('calendar_id', '=', calendar.id),
            ('dayofweek', '=', str(day_date.weekday())),
        ])
        valid_lines = lines.filtered(
            lambda att: not att.date_from or att.date_from <= day_date
        ).filtered(
            lambda att: not att.date_to or att.date_to >= day_date
        ).filtered(
            lambda att: not att.week_type or att.week_type == week_type
        ).filtered(
            lambda att: att.day_period != 'lunch' and att.display_type != 'line_section'
        )

        result = {
            'check_in_utc': False,
            'check_out_utc': False,
            'work_location_id': self.env['zakheni.work.location'],
            'calendar_id': calendar,
            'attendance_lines': valid_lines,
        }

        if not valid_lines:
            # Unscheduled day -> no planned location/hours, but retain the default.
            result['work_location_id'] = self.default_work_location_id
            return result

        earliest = min(float_to_time(att.hour_from) for att in valid_lines)
        latest = max(float_to_time(att.hour_to) for att in valid_lines)

        def _time_to_delta(t):
            return timedelta(
                hours=t.hour, minutes=t.minute,
                seconds=t.second, microseconds=t.microsecond)

        check_in_local = day_local + _time_to_delta(earliest)
        check_out_local = day_local + _time_to_delta(latest)
        # An attendance that crosses midnight yields check_out on the next local day.
        if check_out_local <= check_in_local:
            check_out_local += timedelta(days=1)

        result['check_in_utc'] = check_in_local.astimezone(pytz.utc).replace(tzinfo=None)
        result['check_out_utc'] = check_out_local.astimezone(pytz.utc).replace(tzinfo=None)

        # Prefer the location on the morning line, fall back to the default.
        morning = valid_lines.filtered(lambda att: att.work_location_id) \
            .sorted(key=lambda att: att.hour_from, reverse=True)
        result['work_location_id'] = (
            morning and morning[0].work_location_id
            or self.default_work_location_id
        )

        return result

    def _get_leave_on_date(self, day):
        """Return the first validated hr.leave covering *day* for this employee, or empty."""
        self.ensure_one()
        day_start = datetime.combine(day, dt_time.min)
        day_end = day_start + timedelta(days=1)
        return self.env['hr.leave'].sudo().search([
            ('employee_id', '=', self.id),
            ('state', 'in', ['validate', 'validate1']),
            ('date_from', '<', day_end),
            ('date_to', '>=', day_start),
        ], limit=1)

    def _get_attendance_matrix(self, date_from, date_to):
        """Build the monthly attendance register data for a batch of employees.

        :param date_from/date_to: date objects (inclusive range)
        :returns: list of dicts, one per employee, with
            'employee', 'arrangement', 'days': iterable of per-day dicts
        """
        dates = [date_from + timedelta(days=i) for i in range((date_to - date_from).days + 1)]

        # Batch-load attendances for the whole range once.
        from_dt = datetime.combine(date_from, dt_time.min)
        to_dt = datetime.combine(date_to + timedelta(days=1), dt_time.min)
        attendances = self.env['hr.attendance'].search([
            ('employee_id', 'in', self.ids),
            ('check_in', '>=', from_dt),
            ('check_in', '<', to_dt),
        ], order='check_in asc')

        att_by_emp = {}
        for att in attendances:
            att_by_emp.setdefault(att.employee_id.id, self.env['hr.attendance']).add(att)

        # Local-day grouping per employee.
        rows = []
        for employee in self:
            employee_atts = att_by_emp.get(employee.id, self.env['hr.attendance'])
            tz = pytz.timezone(employee._get_tz())
            att_by_local_day = {}
            for att in employee_atts:
                local = pytz.utc.localize(att.check_in).astimezone(tz).date()
                att_by_local_day.setdefault(local, self.env['hr.attendance']).add(att)

            day_rows = []
            for day in dates:
                day_att = att_by_local_day.get(day, self.env['hr.attendance'])
                schedule = employee._get_hybrid_schedule(day)
                leave = employee._get_leave_on_date(day)
                actual_location = day_att and day_att._get_work_location() or False
                day_rows.append({
                    'date': day,
                    'attendance_ids': day_att.ids,
                    'attendance_count': len(day_att),
                    'leave': leave,
                    'day_type': self._compute_day_type(day, schedule, day_att, leave),
                    'planned_location': schedule.get('work_location_id'),
                    'actual_location': actual_location,
                    'planned_check_in_utc': schedule.get('check_in_utc'),
                    'planned_check_out_utc': schedule.get('check_out_utc'),
                    'worked_hours': sum(att.worked_hours or 0 for att in day_att),
                    'is_late': any(att.is_late for att in day_att),
                    'is_mismatch': any(att.location_mismatch for att in day_att),
                    'is_missing_checkout': any(not att.check_out for att in day_att),
                })

            rows.append({
                'employee': employee,
                'arrangement': employee.work_arrangement,
                'days': day_rows,
            })
        return rows

    def _compute_day_type(self, day, schedule, day_att, leave):
        if leave:
            return 'leave'
        if not schedule:
            return 'unscheduled'
        if not day_att and schedule.get('check_in_utc'):
            return 'absent'
        return 'present'

    @api.model
    def _export_register_xlsx(self, month, year):
        """Build the monthly attendance register spreadsheet (xlsx bytes).

        One row per employee; columns: for each working day (Mon-Fri by default)
        the status (P / L / A / O / U), planned vs actual location, worked hours
        and exception flags. Returns raw xlsx bytes.
        """
        import io

        import xlsxwriter

        first = datetime(year, month, 1)
        if month == 12:
            last = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last = datetime(year, month + 1, 1) - timedelta(days=1)

        employees = self.search([('active', '=', True)])
        rows = employees._get_attendance_matrix(first.date(), last.date())

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        header_format = workbook.add_format(
            {'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'})
        cell_format = workbook.add_format({'border': 1, 'align': 'center'})
        hours_format = workbook.add_format({'border': 1, 'align': 'center', 'num_format': '0.00'})

        summary = workbook.add_worksheet('Summary')
        summary.set_column('A:A', 22)
        summary.set_column('B:B', 40)
        summary.write(0, 0, 'Month', header_format)
        summary.write(0, 1, 'Employees', header_format)
        summary.write(0, 2, 'Working Days', header_format)
        summary.write(1, 0, f'{year:04d}-{month:02d}', cell_format)
        summary.write(1, 1, len(rows), cell_format)
        working_days = 0
        if rows:
            working_days = sum(
                1 for d in rows[0]['days'] if d['day_type'] != 'day_off')
        summary.write(1, 2, working_days, cell_format)

        register = workbook.add_worksheet('Register')
        headers = ['Employee', 'Arrangement']
        if rows:
            headers += [f'{d["date"].day}' for d in rows[0]['days']]
        headers += ['Worked Hours', 'Exceptions']
        register.set_column(0, 0, 24)
        register.set_column(1, 1, 14)
        for col, header in enumerate(headers):
            register.write(0, col, header, header_format)

        row_idx = 1
        for emp_row in rows:
            register.write(row_idx, 0, emp_row['employee'].name, cell_format)
            register.write(row_idx, 1, emp_row['arrangement'] or '', cell_format)
            for col_offset, day in enumerate(emp_row['days']):
                status = {
                    'present': 'P',
                    'absent': 'A',
                    'leave': 'L',
                    'day_off': 'O',
                    'unscheduled': 'U',
                }.get(day['day_type'], '?')
                register.write(row_idx, 2 + col_offset, status, cell_format)
            totals = sum(day['worked_hours'] for day in emp_row['days'])
            exceptions = sum(
                1 for day in emp_row['days']
                if day['is_late'] or day['is_mismatch'] or day['is_missing_checkout']
            )
            register.write(row_idx, 2 + len(emp_row['days']), round(totals, 2), hours_format)
            register.write(row_idx, 3 + len(emp_row['days']), exceptions, cell_format)
            row_idx += 1

        workbook.close()
        return output.getvalue()
