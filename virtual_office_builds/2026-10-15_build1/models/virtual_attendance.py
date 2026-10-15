"""Attendance + device-presence integration for the Virtual Office.

Auto clock-in/out
-----------------
When a logged-in user enters an office (an attendee session is created) and
the office has ``attendance_enabled`` set, the user's employee is checked in
via ``hr.attendance``. Leaving the office (or being reaped as stale) checks
them out again. Guests and users without an employee record are skipped, and
an employee who is already clocked in elsewhere (kiosk, another office) is
never double-checked-in.

If the ``zakheni_hybrid_attendance`` module is installed, the check-in is
mapped to a ``zakheni.work.location`` (found or auto-created per office,
type "home"/WFH) so the hybrid dashboard's location split and mismatch logic
see virtual-office work as remote work.

Device-presence monitoring
--------------------------
Each attendee reports a client state on every heartbeat: ``online`` (tab
focused and active), ``idle`` (tab hidden) or ``away`` (no mouse/keyboard
activity in the tab for a while). Combined with ``last_seen`` staleness this
drives a ``device_status`` (present / idle / away / gone) and an
``away_minutes`` counter, surfaced in the office UI and in the backend
attendee list so managers can see who is clocked in but not at their device.
"""

import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# An attendee that has not sent a heartbeat within this many seconds is
# considered gone (browser closed, network dropped, laptop slept).
STALE_SECONDS = 45


class VirtualAttendeeAttendance(models.Model):
    _inherit = "virtual.attendee"

    # ------------------------------------------------------------- attendance
    attendance_id = fields.Many2one(
        "hr.attendance",
        string="Attendance",
        ondelete="set null",
        copy=False,
        help="The hr.attendance record opened by this office session (if any).",
    )
    clocked_in = fields.Boolean(
        string="Clocked in",
        compute="_compute_clocked_in",
        search="_search_clocked_in",
        help="Whether the attendee's employee currently has an open attendance.",
    )

    # ------------------------------------------------------ device monitoring
    away_since = fields.Datetime(
        string="Away since",
        help="When the attendee last went idle/away (cleared when back online).",
    )
    away_minutes = fields.Integer(
        string="Away (min)",
        compute="_compute_away_minutes",
        help="Minutes the attendee has been away from their device.",
    )
    device_status = fields.Selection(
        [
            ("present", "At device"),
            ("idle", "Idle (tab hidden)"),
            ("away", "Away"),
            ("gone", "Gone (no heartbeat)"),
        ],
        string="Device status",
        compute="_compute_device_status",
        search="_search_device_status",
    )

    # ------------------------------------------------------------- attendance
    @api.depends("user_id", "user_id.employee_id")
    def _compute_clocked_in(self):
        for att in self:
            emp = att.user_id.employee_id
            if not emp:
                att.clocked_in = False
                continue
            att.clocked_in = bool(
                self.env["hr.attendance"]
                .sudo()
                .search_count(
                    [("employee_id", "=", emp.id), ("check_out", "=", False)]
                )
            )

    @api.model
    def _search_clocked_in(self, operator, value):
        emp_ids = (
            self.env["hr.attendance"]
            .sudo()
            .search([("check_out", "=", False)])
            .employee_id.ids
        )
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [("user_id.employee_id", "in", emp_ids)]
        return [("user_id.employee_id", "not in", emp_ids)]

    def _resolve_work_location(self, office):
        """Find or create the zakheni work location mapped to this office.

        Only meaningful when ``zakheni_hybrid_attendance`` is installed; the
        model is looked up defensively so the module still works without it.
        """
        if "zakheni.work.location" not in self.env.registry.models:
            return False
        loc_model = self.env["zakheni.work.location"].sudo()
        loc = loc_model.search(
            [
                ("name", "=", office.name),
                ("company_id", "=", office.company_id.id),
            ],
            limit=1,
        )
        if not loc:
            loc = loc_model.create(
                {
                    "name": office.name,
                    "code": office.code or "virtual-office",
                    "location_type": "home",
                    "company_id": office.company_id.id,
                }
            )
        return loc

    def _clock_in(self):
        """Open an hr.attendance for the attendee's employee (if eligible)."""
        for att in self:
            if not att.office_id.attendance_enabled:
                continue
            emp = att.user_id.employee_id
            if not emp:
                continue
            att_model = self.env["hr.attendance"].sudo()
            open_att = att_model.search(
                [("employee_id", "=", emp.id), ("check_out", "=", False)], limit=1
            )
            if open_att:
                # Already clocked in elsewhere (kiosk, another office): never
                # create an overlapping attendance.
                continue
            vals = {
                "employee_id": emp.id,
                "check_in": fields.Datetime.now(),
            }
            if "work_location_id" in att_model._fields:
                loc = self._resolve_work_location(att.office_id)
                if loc:
                    vals["work_location_id"] = loc.id
                if "capture_method" in att_model._fields:
                    vals["capture_method"] = "manual"
            att.attendance_id = att_model.create(vals)
            _logger.info(
                "Virtual Office: clocked in %s via office %s (attendance %s)",
                emp.name, att.office_id.name, att.attendance_id.id,
            )

    def _clock_out(self):
        """Close the attendance this session opened, if it is still open."""
        for att in self:
            if att.attendance_id and not att.attendance_id.check_out:
                att.attendance_id.sudo().write(
                    {"check_out": fields.Datetime.now()}
                )
                _logger.info(
                    "Virtual Office: clocked out %s (attendance %s)",
                    att.name, att.attendance_id.id,
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._clock_in()
        return records

    def leave(self):
        res = super().leave()
        self._clock_out()
        return res

    @api.model
    def _reap_stale(self):
        limit = fields.Datetime.now() - timedelta(seconds=STALE_SECONDS)
        stale = self.sudo().search(
            [("state", "!=", "offline"), ("last_seen", "<", limit)]
        )
        if stale:
            _logger.info("Virtual Office: reaping %s stale attendees", len(stale))
            stale.write({"state": "offline", "camera_on": False, "mic_on": False})
            stale._clock_out()
        return len(stale)

    # ------------------------------------------------------ device monitoring
    @api.depends("state", "away_since", "last_seen")
    def _compute_away_minutes(self):
        now = fields.Datetime.now()
        for att in self:
            if att.state in ("idle", "away") and att.away_since:
                att.away_minutes = int((now - att.away_since).total_seconds() // 60)
            elif (
                att.state == "online"
                and att.last_seen
                and (now - att.last_seen).total_seconds() > STALE_SECONDS
            ):
                att.away_minutes = int((now - att.last_seen).total_seconds() // 60)
            else:
                att.away_minutes = 0

    @api.depends("state", "last_seen")
    def _compute_device_status(self):
        now = fields.Datetime.now()
        for att in self:
            if att.state == "offline":
                att.device_status = "gone"
            elif att.state in ("idle", "away"):
                att.device_status = att.state
            elif att.last_seen and (now - att.last_seen).total_seconds() > STALE_SECONDS:
                att.device_status = "gone"
            else:
                att.device_status = "present"

    @api.model
    def _search_device_status(self, operator, value):
        values = value if isinstance(value, (list, tuple)) else [value]
        if operator in ("=", "in"):
            wanted = set(values)
        elif operator in ("!=", "not in"):
            wanted = set(self._fields["device_status"].selection) - set(values)
        else:
            raise NotImplementedError("Unsupported operator %r" % operator)
        limit = fields.Datetime.now() - timedelta(seconds=STALE_SECONDS)
        groups = []
        if "present" in wanted:
            groups.append(
                ["&", ("state", "=", "online"), ("last_seen", ">=", limit)]
            )
        if "idle" in wanted:
            groups.append([("state", "=", "idle")])
        if "away" in wanted:
            groups.append([("state", "=", "away")])
        if "gone" in wanted:
            groups.append(
                ["|", ("state", "=", "offline"), ("last_seen", "<", limit)]
            )
        if not groups:
            return [("id", "=", False)]
        if len(groups) == 1:
            return groups[0]
        # OR-chain the groups in flat prefix notation: n-1 '|' separators
        # first, then every group's leaves/operators inlined. Interleaving
        # the separators breaks the operator/operand balance (a group that
        # already starts with '|' or '&' would add a dangling operator).
        flat = ["|"] * (len(groups) - 1)
        for group in groups:
            flat.extend(group)
        return flat

    def heartbeat(self, data):
        res = super().heartbeat(data)
        for att in self:
            if att.state in ("idle", "away") and not att.away_since:
                att.away_since = fields.Datetime.now()
            elif att.state == "online" and att.away_since:
                att.away_since = False
        return res

    def get_public_data(self):
        data = super().get_public_data()
        data["device_status"] = self.device_status
        data["away_minutes"] = self.away_minutes
        return data