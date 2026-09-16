from odoo import fields, models


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    work_location_id = fields.Many2one(
        'zakheni.work.location', string="Work Location",
        help="Planned work location for this schedule line. Used to build the "
             "planned vs actual location comparison.")
