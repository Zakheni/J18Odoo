from datetime import timedelta

import pytz
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    work_location_id = fields.Many2one(
        'zakheni.work.location', string="Work Location",
        help="Actual location where the employee clocked in, auto-detected "
             "from GPS/IP or manually selected.")
    capture_method = fields.Selection([
        ('ip', 'IP Address'),
        ('gps', 'GPS'),
        ('manual', 'Manual'),
    ], string="Capture Method", default='manual',
        help="How the check-in location was captured.")
    glat = fields.Float(string="GPS Latitude", digits=(10, 7), readonly=True,
        help="GPS latitude recorded at check-in.")
    glon = fields.Float(string="GPS Longitude", digits=(10, 7), readonly=True,
        help="GPS longitude recorded at check-in.")
    gacc = fields.Float(string="GPS Accuracy (m)", digits=(16, 2), readonly=True,
        help="GPS accuracy reported by the device at check-in (metres).")
    is_late = fields.Boolean(string="Late Check-In", compute='_compute_hybrid_flags', store=True)
    late_minutes = fields.Float(
        string="Late (minutes)", compute='_compute_hybrid_flags', store=True)
    location_mismatch = fields.Boolean(
        string="Location Mismatch", compute='_compute_hybrid_flags', store=True)
    is_exception = fields.Boolean(string="Exception", compute='_compute_hybrid_flags', store=True)
    exception_text = fields.Char(
        string="Exception Details", compute='_compute_hybrid_flags', store=True)
    planned_location_id = fields.Many2one(
        'zakheni.work.location', string="Planned Work Location",
        compute='_compute_planned_check_in_out', store=True,
        help="Location planned for this attendance from the work schedule.")
    planned_check_in_utc = fields.Datetime(compute='_compute_planned_check_in_out', store=True)
    planned_check_out_utc = fields.Datetime(compute='_compute_planned_check_in_out', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
        ('corrected', 'Corrected'),
    ], string="Status", default='draft', tracking=True)

    def _get_day_date(self):
        """Local calendar date of this attendance for the employee."""
        self.ensure_one()
        tz = pytz.timezone(self.employee_id._get_tz())
        return pytz.utc.localize(self.check_in).astimezone(tz).date()

    @api.depends('check_in', 'employee_id')
    def _compute_planned_check_in_out(self):
        for att in self:
            if not att.employee_id:
                att.planned_check_in_utc = False
                att.planned_check_out_utc = False
                att.planned_location_id = False
                continue
            schedule = att.employee_id._get_hybrid_schedule(att._get_day_date())
            att.planned_check_in_utc = schedule.get('check_in_utc')
            att.planned_check_out_utc = schedule.get('check_out_utc')
            att.planned_location_id = schedule.get('work_location_id')

    @api.depends('check_in', 'check_out', 'planned_check_in_utc', 'planned_check_out_utc',
                 'work_location_id', 'planned_location_id')
    def _compute_hybrid_flags(self):
        for att in self:
            late = False
            late_minutes = 0.0
            if att.check_in and att.planned_check_in_utc:
                grace = att.employee_id.company_id.zakheni_late_grace_minutes
                if att.check_in > att.planned_check_in_utc + timedelta(minutes=grace):
                    later = att.check_in - att.planned_check_in_utc
                    late = True
                    late_minutes = round(later.total_seconds() / 60.0, 1)

            mismatch = False
            if (
                att.work_location_id
                and att.planned_location_id
                and att.work_location_id != att.planned_location_id
            ):
                mismatch = True

            exceptions = []
            if late:
                exceptions.append(_('Late'))
            if mismatch:
                exceptions.append(_('Wrong location'))
            if not att.check_out:
                exceptions.append(_('No check-out'))

            att.is_late = late
            att.late_minutes = late_minutes
            att.location_mismatch = mismatch
            att.is_exception = bool(exceptions)
            att.exception_text = ', '.join(exceptions)

    @api.model
    def _detect_work_location_values(self, vals):
        """Best-effort detection of the work location for a check-in/check-out."""
        lat = vals.get('in_latitude') or vals.get('out_latitude') or 0.0
        lon = vals.get('in_longitude') or vals.get('out_longitude') or 0.0
        location = self.env['zakheni.work.location'].detect(lat, lon)
        has_ip = vals.get('in_ip_address') or vals.get('out_ip_address')
        capture = 'gps' if (lat and lon) else ('ip' if has_ip else 'manual')
        return {'work_location_id': location.id or False, 'capture_method': capture}

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('work_location_id'):
                values = self._detect_work_location_values(vals)
                vals.update(values)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('check_out') and not vals.get('work_location_id'):
            for att in self.filtered(lambda a: not a.check_out and not a.work_location_id):
                values = att._detect_work_location_values(vals)
                if values.get('work_location_id'):
                    att.work_location_id = values['work_location_id']
        return super().write(vals)

    @api.constrains('check_in', 'check_out')
    def _check_validity_check_in_check_out(self):
        super()._check_validity_check_in_check_out()

    def _get_work_location(self):
        """Return the effective work location across this attendance set (latest wins)."""
        atts = self.filtered(lambda a: a.work_location_id)
        if atts:
            return atts[-1].work_location_id
        return self.browse()

    def action_approve(self):
        for att in self:
            att.state = 'approved'

    def action_refuse(self):
        for att in self:
            att.state = 'refused'

    def action_set_corrected(self):
        for att in self:
            att.state = 'corrected'

    def button_open_planned(self):
        self.ensure_one()
        if not self.planned_location_id:
            raise UserError(_("No planned location for this attendance's day."))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'zakheni.work.location',
            'res_id': self.planned_location_id.id,
            'view_mode': 'form',
        }
