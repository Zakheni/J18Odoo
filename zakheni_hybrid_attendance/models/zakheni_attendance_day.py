from datetime import datetime, timedelta
from datetime import time as dt_time

import pytz
from odoo import api, fields, models


class ZakheniAttendanceDay(models.Model):
    _name = "zakheni.attendance.day"
    _description = "Daily Work Record"
    _order = "employee_id, date desc"
    _rec_name = "display_name"

    employee_id = fields.Many2one(
        'hr.employee', string="Employee", required=True,
        ondelete='cascade', index=True)
    date = fields.Date(string="Date", required=True, index=True)
    day_type = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('leave', 'On Leave'),
        ('day_off', 'Day Off'),
        ('unscheduled', 'Unscheduled'),
    ], string="Day Type", compute='_compute_day', store=False)
    is_working_day = fields.Boolean(
        string="Scheduled Working Day", compute='_compute_day', store=False,
        help="A day the employee is scheduled to work according to their calendar.")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], string="Status", default='draft')
    planned_location_id = fields.Many2one('zakheni.work.location', string="Planned Location")
    actual_location_id = fields.Many2one('zakheni.work.location', string="Actual Location")
    location_mismatch = fields.Boolean(
        string="Location Mismatch", compute='_compute_day',
        search='_search_location_mismatch')
    is_late = fields.Boolean(string="Late", compute='_compute_day', search='_search_is_late')
    late_minutes = fields.Float(string="Late (minutes)", compute='_compute_day', store=False)
    missing_checkout = fields.Boolean(
        string="No Check-Out", compute='_compute_day', search='_search_missing_checkout')
    is_exception = fields.Boolean(
        string="Exception", compute='_compute_day', search='_search_is_exception')
    exception_text = fields.Char(string="Exceptions", compute='_compute_day')
    planned_check_in_utc = fields.Datetime(string="Planned Check-In")
    planned_check_out_utc = fields.Datetime(string="Planned Check-Out")
    first_check_in_utc = fields.Datetime(string="First Check-In")
    last_check_out_utc = fields.Datetime(string="Last Check-Out")
    worked_hours = fields.Float(string="Worked Hours", compute='_compute_day', store=False)
    attendance_count = fields.Integer(string="Slots", compute='_compute_day')
    attendance_ids = fields.One2many(
        'hr.attendance', 'employee_id', string="Attendances",
        compute='_compute_attendance_ids', store=False)
    leave_id = fields.Many2one('hr.leave', string="Leave", compute='_compute_day')
    note = fields.Char(string="Note")

    display_name = fields.Char(compute='_compute_display_name')

    _sql_constraints = [
        ('employee_date_uniq', 'UNIQUE (employee_id, date)',
         "A daily work record already exists for this employee on this date."),
    ]

    @api.depends('employee_id')
    def _compute_attendance_ids(self):
        for record in self:
            tz = pytz.timezone(record.employee_id._get_tz() or 'UTC')
            day_start_local = tz.localize(datetime.combine(record.date, dt_time.min))
            day_end_local = day_start_local + timedelta(days=1)
            record.attendance_ids = self.env['hr.attendance'].search([
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', day_start_local.astimezone(pytz.utc).replace(tzinfo=None)),
                ('check_in', '<', day_end_local.astimezone(pytz.utc).replace(tzinfo=None)),
            ])

    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.employee_id.name} - {record.date}"

    @api.model
    def _day_domain_from_attendances(self, attendances):
        """Domain over zakheni.attendance.day for the (employee, local date) of each attendance."""
        pairs = set()
        for att in attendances:
            tz = pytz.timezone(att.employee_id._get_tz() or 'UTC')
            local_date = pytz.utc.localize(att.check_in).astimezone(tz).date()
            pairs.add((att.employee_id.id, local_date))
        if not pairs:
            return [('id', '=', False)]
        domains = [[('employee_id', '=', e), ('date', '=', d)] for e, d in pairs]
        return ['|'] * (len(domains) - 1) + domains

    @api.model
    def _search_is_exception(self, operator, value):
        atts = self.env['hr.attendance'].search(
            [('is_exception', operator, value)], order='check_in asc')
        return self._day_domain_from_attendances(atts)

    @api.model
    def _search_is_late(self, operator, value):
        atts = self.env['hr.attendance'].search(
            [('is_late', operator, value)], order='check_in asc')
        return self._day_domain_from_attendances(atts)

    @api.model
    def _search_location_mismatch(self, operator, value):
        atts = self.env['hr.attendance'].search(
            [('location_mismatch', operator, value)], order='check_in asc')
        return self._day_domain_from_attendances(atts)

    @api.model
    def _search_missing_checkout(self, operator, value):
        atts = self.env['hr.attendance'].search(
            [('check_out', '=', False)], order='check_in asc')
        return self._day_domain_from_attendances(atts)

    @api.depends('planned_check_in_utc', 'planned_check_out_utc', 'attendance_ids')
    def _compute_day(self):
        for record in self:
            atts = record.attendance_ids
            record.leave_id = record.employee_id._get_leave_on_date(record.date)
            worked = sum(att.worked_hours or 0 for att in atts)
            record.worked_hours = round(worked, 2)
            record.attendance_count = len(atts)
            record.is_late = any(att.is_late for att in atts)
            record.late_minutes = max((att.late_minutes or 0.0) for att in atts) if atts else 0.0
            record.missing_checkout = any(not att.check_out for att in atts)
            record.location_mismatch = any(att.location_mismatch for att in atts)
            record.is_exception = (
                record.is_late or record.missing_checkout or record.location_mismatch
            )
            record.exception_text = ', '.join(filter(None, [
                'Late' if record.is_late else '',
                'No check-out' if record.missing_checkout else '',
                'Location mismatch' if record.location_mismatch else '',
            ]))
            record.first_check_in_utc = atts[0].check_in if atts else False
            last_checkout = max(
                (att.check_out for att in atts if att.check_out), default=False)
            record.last_check_out_utc = last_checkout

            planned = record.planned_check_in_utc and record.planned_check_out_utc
            record.is_working_day = bool(planned)
            if record.leave_id:
                record.day_type = 'leave'
            elif not planned and not atts:
                record.day_type = 'day_off'
            elif atts:
                record.day_type = 'present'
            elif planned:
                record.day_type = 'absent'
            else:
                record.day_type = 'unscheduled'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record._refresh_planned()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'planned_check_in_utc' not in vals:
            for record in self:
                record._refresh_planned()
        return res

    def _refresh_planned(self):
        """Sync planned values from the employee's hybrid schedule."""
        for record in self:
            schedule = record.employee_id._get_hybrid_schedule(record.date)
            if not schedule:
                continue
            vals = {
                'planned_check_in_utc': schedule.get('check_in_utc'),
                'planned_check_out_utc': schedule.get('check_out_utc'),
                'planned_location_id': schedule.get('work_location_id').id or False,
            }
            super(ZakheniAttendanceDay, record).write(vals)

    def action_approve(self):
        for record in self:
            record.state = 'approved'

    def action_refuse(self):
        for record in self:
            record.state = 'refused'

    def action_recompute(self):
        for record in self:
            record._refresh_planned()
            record.note = False

    @api.model
    def _cron_build_daily_records(self):
        """Roll-up cron: build daily records for the previous local day for all active employees."""
        day = fields.Date.today() - timedelta(days=1)
        employees = self.env['hr.employee'].sudo().search([('active', '=', True)])
        for employee in employees:
            self._ensure_daily_record(employee, day)
        return True

    @api.model
    def _cron_today_snapshot(self):
        """Build today's records as employees check in (called during check-in hook / periodic)."""
        self._ensure_daily_record_for_all(fields.Date.today())
        return True

    @api.model
    def _ensure_daily_record_for_all(self, day):
        """Create missing daily records for *day* (local) for every active employee."""
        employees = self.env['hr.employee'].sudo().search([('active', '=', True)])
        for employee in employees:
            self._ensure_daily_record(employee, day)

    @api.model
    def _ensure_daily_record(self, employee, day):
        """Create the daily record for *employee* on *day* if it does not exist yet."""
        existing = self.sudo().search([
            ('employee_id', '=', employee.id),
            ('date', '=', day),
        ], limit=1)
        if existing:
            return existing
        schedule = employee._get_hybrid_schedule(day)
        return self.sudo().create({
            'employee_id': employee.id,
            'date': day,
            'planned_check_in_utc': schedule.get('check_in_utc'),
            'planned_check_out_utc': schedule.get('check_out_utc'),
            'planned_location_id': schedule.get('work_location_id').id or False,
        })

    @api.model
    def _get_dashboard_data(self):
        """Live dashboard payload: counts per status, per location type, and exception tallies."""
        employee = self.env.user.employee_id
        tz = pytz.timezone(employee._get_tz() if employee else 'UTC')
        now_utc = fields.Datetime.now()
        now = pytz.utc.localize(now_utc).astimezone(tz)
        today = now.date()

        employees = self.env['hr.employee'].sudo().search([('active', '=', True)])
        present = self.env['hr.attendance'].sudo().search([('check_out', '=', False)]).employee_id
        on_leave = self.env['hr.employee'].sudo().browse(
            [e.id for e in employees if e._get_leave_on_date(today)])

        scheduled = []
        for emp in employees:
            sch = emp._get_hybrid_schedule(today)
            if sch.get('check_in_utc'):
                scheduled.append(emp)
        scheduled_set = self.env['hr.employee'].browse([e.id for e in scheduled])

        absent = scheduled_set - present - on_leave
        day_off = employees - scheduled_set - on_leave

        # Attendance data for today (local tz) split by work location type.
        day_start = tz.localize(datetime.combine(today, dt_time.min))
        day_start = day_start.astimezone(pytz.utc).replace(tzinfo=None)
        day_end = tz.localize(datetime.combine(today + timedelta(days=1), dt_time.min))
        day_end = day_end.astimezone(pytz.utc).replace(tzinfo=None)
        today_atts = self.env['hr.attendance'].sudo().search([
            ('check_in', '>=', day_start), ('check_in', '<', day_end),
        ])
        open_atts = today_atts.filtered(lambda a: not a.check_out)

        location_map = {}
        for att in open_atts:
            loc = att.work_location_id
            key = loc.location_type if loc else 'no_location'
            location_map.setdefault(key, 0)
            location_map[key] += 1

        late = today_atts.filtered(lambda a: a.is_late)
        mismatched = today_atts.filtered(lambda a: a.location_mismatch)
        missing_checkout = today_atts.filtered(lambda a: not a.check_out)

        pending = self.search([('state', '=', 'draft'), ('is_exception', '=', True)])

        return {
            'today': str(today),
            'day_offset': str(now.isoformat()),
            'total_employees': len(employees),
            'scheduled': len(scheduled),
            'present': len(present & scheduled_set),
            'on_leave': len(on_leave),
            'day_off': len(day_off),
            'absent': len(absent),
            'not_scheduled_present': len(present - scheduled_set),
            'locations': location_map,
            'late_count': len(late),
            'mismatch_count': len(mismatched),
            'missing_checkout_count': len(missing_checkout),
            'pending_exception_count': len(pending),
        }
