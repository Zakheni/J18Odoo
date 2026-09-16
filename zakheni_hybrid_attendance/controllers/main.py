# Part of Zakheni. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import _, http
from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.exceptions import UserError
from odoo.http import request


class ZakheniHybridAttendance(http.Controller):

    def _get_geoip(self, mode, latitude=False, longitude=False):
        return HrAttendance._get_geoip_response(mode, latitude=latitude, longitude=longitude)

    @http.route('/zakheni_attendance/check', type='json', auth='user')
    def hybrid_check(
        self,
        latitude=False,
        longitude=False,
        accuracy=False,
        work_location_id=False,
        capture_method=False,
    ):
        """Check-in/check-out that also captures the work location.

        Auto-detects the location from GPS if none is supplied, otherwise uses
        the explicitly selected one. Snaps a daily record for today.
        """
        employee = request.env.user.employee_id
        if not employee:
            raise UserError(_(
                "Your user is not linked to an employee, so you cannot check in or out."
            ))

        geo = self._get_geoip('systray', latitude=latitude, longitude=longitude)
        attendance = employee._attendance_action_change(geo)
        if not attendance:
            return False

        if not attendance.check_out:
            # Just checked in -> record location + GPS info.
            vals = {
                'glat': latitude or attendance.in_latitude or 0.0,
                'glon': longitude or attendance.in_longitude or 0.0,
                'gacc': accuracy or 0.0,
                'capture_method': capture_method or (latitude and 'gps' or 'ip'),
            }
            if work_location_id:
                vals['work_location_id'] = work_location_id
            attendance.write(vals)

        # Ensure today's daily record exists (planned vs actual comparison).
        request.env['zakheni.attendance.day']._cron_today_snapshot()
        return {
            'attendance_id': attendance.id,
            'checked_in': not attendance.check_out,
            'work_location_id': attendance.work_location_id.id or False,
            'work_location_type': attendance.work_location_id.location_type or False,
            'is_late': attendance.is_late,
            'location_mismatch': attendance.location_mismatch,
            'exception_text': attendance.exception_text,
        }

    @http.route('/zakheni_attendance/whitelist_employees', type='json', auth='user')
    def whitelist_employees(self):
        """Names + ids of employees the user may act for (self, or all for managers)."""
        is_manager = request.env.user.has_group(
            'zakheni_hybrid_attendance.group_zakheni_attendance_manager'
        )
        domain = [] if is_manager else [('id', '=', request.env.user.employee_id.id)]
        employees = request.env['hr.employee'].sudo().search(domain)
        return [{'id': emp.id, 'name': emp.name} for emp in employees]

    @http.route('/zakheni_attendance/live', type='json', auth='user')
    def live_dashboard(self):
        """JSON payload for the live attendance dashboard."""
        if not request.env.user.has_group(
            'zakheni_hybrid_attendance.group_zakheni_attendance_manager'
        ):
            raise UserError(_("You do not have access to the attendance dashboard."))
        return request.env['zakheni.attendance.day']._get_dashboard_data()

    @http.route('/zakheni_attendance/register_export', type='http', auth='user')
    def register_export(self, month=False, year=False):
        """Generate the monthly attendance register as an .xlsx file."""
        if not request.env.user.has_group(
            'zakheni_hybrid_attendance.group_zakheni_attendance_manager'
        ):
            raise UserError(_("You do not have access to the attendance register."))
        try:
            month = int(month) if month else False
            year = int(year) if year else False
        except (TypeError, ValueError):
            month = year = False
        now = datetime.now()
        month = month or now.month
        year = year or now.year

        data = request.env['hr.employee'].sudo()._export_register_xlsx(month, year)
        filename = f'attendance_register_{year:04d}_{month:02d}.xlsx'
        return request.make_response(
            data,
            headers=[
                (
                    'Content-Type',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                ),
                ('Content-Disposition', f'attachment; filename={filename}'),
            ],
        )
