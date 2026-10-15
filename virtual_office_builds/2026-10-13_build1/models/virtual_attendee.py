import logging
import secrets
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# An attendee that has not sent a heartbeat within this many seconds is
# considered gone (browser closed, network dropped, laptop slept).
STALE_SECONDS = 45


class VirtualAttendee(models.Model):
    _name = "virtual.attendee"
    _description = "Virtual Office Attendee (live presence)"
    _order = "room_id, name"
    _rec_name = "name"

    name = fields.Char(compute="_compute_name", store=True)
    user_id = fields.Many2one("res.users", ondelete="cascade", index=True)
    partner_id = fields.Many2one(related="user_id.partner_id", store=True)
    guest_pass_id = fields.Many2one("virtual.guest.pass", ondelete="cascade")
    is_guest = fields.Boolean(compute="_compute_is_guest", store=True)
    is_manager = fields.Boolean(compute="_compute_is_manager")

    office_id = fields.Many2one(
        "virtual.office", required=True, ondelete="cascade", index=True
    )
    room_id = fields.Many2one(
        "virtual.room", ondelete="set null", index=True, string="Current room"
    )
    company_id = fields.Many2one(related="office_id.company_id", store=True)

    access_token = fields.Char(
        default=lambda self: secrets.token_urlsafe(24), copy=False, index=True
    )
    peer_id = fields.Char(
        default=lambda self: secrets.token_hex(8), copy=False, index=True
    )

    # --- live state ---
    state = fields.Selection(
        [
            ("online", "Online"),
            ("idle", "Idle"),
            ("away", "Away"),
            ("offline", "Offline"),
        ],
        default="online",
        index=True,
    )
    pos_x = fields.Float(default=0.0)
    pos_y = fields.Float(default=0.0)
    pos_z = fields.Float(default=0.0)
    rotation_y = fields.Float(default=0.0)
    camera_on = fields.Boolean(default=False)
    mic_on = fields.Boolean(default=False)
    screen_sharing = fields.Boolean(default=False)
    is_speaking = fields.Boolean(default=False)
    color = fields.Char(default="#7C4DFF")
    avatar_seed = fields.Integer(default=lambda self: secrets.randbelow(1000))

    session_start = fields.Datetime(default=fields.Datetime.now)
    last_seen = fields.Datetime(default=fields.Datetime.now, index=True)

    _sql_constraints = [
        (
            "access_token_uniq",
            "unique(access_token)",
            "The attendee session token must be unique.",
        ),
    ]

    # -------------------------------------------------------------- computes
    @api.depends("user_id", "guest_pass_id", "guest_pass_id.name")
    def _compute_name(self):
        for att in self:
            if att.user_id:
                att.name = att.user_id.name
            elif att.guest_pass_id:
                att.name = "%s (guest)" % (att.guest_pass_id.name or "Guest")
            else:
                att.name = "Guest"

    @api.depends("guest_pass_id")
    def _compute_is_guest(self):
        for att in self:
            att.is_guest = bool(att.guest_pass_id)

    @api.depends("user_id")
    def _compute_is_manager(self):
        mgr_group = self.env.ref(
            "virtual_office.group_virtual_office_manager", raise_if_not_found=False
        )
        for att in self:
            att.is_manager = bool(
                att.user_id and mgr_group and att.user_id in mgr_group.users
            )

    # ------------------------------------------------------------------ API
    @api.model
    def authenticate(self, token):
        """Resolve a live attendee from its session token. Returns a record or empty.

        Offline sessions (left the office or reaped as stale) are rejected so a
        stale token cannot keep heart-beating.
        """
        if not token:
            return self.browse()
        att = (
            self.sudo()
            .search(
                [("access_token", "=", token), ("state", "!=", "offline")],
                limit=1,
            )
            .exists()
        )
        return att

    @api.model
    def join(self, office, room=None, user=None, guest_pass=None):
        """Create a fresh attendee session for a user or guest pass."""
        office = office.sudo()
        if room is None:
            room = office._ensure_lobby()
        if not office.room_ids:
            room = office._ensure_lobby()
        # If the requested room is private, fall back to the lobby.
        if room and room.is_private:
            allowed = room.allowed_user_ids
            if not (user and (user in allowed or user.has_group(
                "virtual_office.group_virtual_office_manager"
            ))):
                room = office._ensure_lobby()

        vals = {
            "office_id": office.id,
            "room_id": room.id if room else False,
            "state": "online",
            "last_seen": fields.Datetime.now(),
            "session_start": fields.Datetime.now(),
            "color": office.brand_color or "#7C4DFF",
            "pos_x": room.pos_x if room else 0.0,
            "pos_y": room.pos_y if room else 0.0,
        }
        if user and not user._is_public():
            vals["user_id"] = user.id
        if guest_pass:
            vals["guest_pass_id"] = guest_pass.id
        return self.sudo().create(vals)

    def heartbeat(self, data):
        """Update live state from a client heartbeat and return peers to sync."""
        self.ensure_one()
        writable = {
            "pos_x",
            "pos_y",
            "pos_z",
            "rotation_y",
            "state",
            "camera_on",
            "mic_on",
            "screen_sharing",
            "is_speaking",
        }
        vals = {k: v for k, v in (data or {}).items() if k in writable}
        if "state" in vals and vals["state"] not in ("online", "idle", "away", "offline"):
            vals.pop("state")
        vals["last_seen"] = fields.Datetime.now()
        # Move room if requested and allowed.
        room_id = (data or {}).get("room_id")
        if room_id and room_id != self.room_id.id:
            room = self.env["virtual.room"].sudo().browse(int(room_id)).exists()
            if room and room.office_id == self.office_id and not room.is_private:
                vals["room_id"] = room.id
        self.sudo().write(vals)
        return self

    def leave(self):
        for att in self:
            att.sudo().write({"state": "offline", "camera_on": False, "mic_on": False})

    def get_public_data(self):
        self.ensure_one()
        return {
            "peer_id": self.peer_id,
            "name": self.name,
            "is_guest": self.is_guest,
            "is_me": False,
            "room_id": self.room_id.id if self.room_id else False,
            "state": self.state,
            "position": {"x": self.pos_x, "y": self.pos_y, "z": self.pos_z},
            "rotation_y": self.rotation_y,
            "camera_on": self.camera_on,
            "mic_on": self.mic_on,
            "screen_sharing": self.screen_sharing,
            "is_speaking": self.is_speaking,
            "color": self.color,
            "avatar_seed": self.avatar_seed,
        }

    @api.model
    def _reap_stale(self):
        limit = fields.Datetime.now() - timedelta(seconds=STALE_SECONDS)
        stale = self.sudo().search(
            [("state", "!=", "offline"), ("last_seen", "<", limit)]
        )
        if stale:
            _logger.info("Virtual Office: reaping %s stale attendees", len(stale))
            stale.write({"state": "offline", "camera_on": False, "mic_on": False})
        return len(stale)
