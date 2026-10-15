import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class VirtualOffice(models.Model):
    _name = "virtual.office"
    _description = "Virtual Office"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(
        help="Short URL slug for this office. Used in pretty links, e.g. /virtual-office/my-hq",
        copy=False,
    )
    description = fields.Html()
    company_id = fields.Many2one(
        "res.company", required=True, default=lambda self: self.env.company, index=True
    )
    manager_id = fields.Many2one(
        "res.users",
        string="Manager",
        default=lambda self: self.env.user,
        domain="[('share', '=', False)]",
    )
    member_ids = fields.Many2many(
        "res.users",
        "virtual_office_member_rel",
        "office_id",
        "user_id",
        string="Members",
        help="Users allowed to enter this office. Managers and admins always may.",
    )
    is_public = fields.Boolean(
        string="Allow guest links",
        default=True,
        help="If set, guest passes can be generated to let external people in without an account.",
    )
    attendance_enabled = fields.Boolean(
        string="Auto clock-in/out",
        default=True,
        help="When enabled, entering this office checks the user in (hr.attendance) "
             "and leaving checks them out.",
    )
    access_token = fields.Char(
        "Public link token", copy=False, default=lambda self: self._default_access_token(), readonly=True
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], default="open", required=True
    )

    room_ids = fields.One2many("virtual.room", "office_id", string="Rooms")
    attendee_ids = fields.One2many(
        "virtual.attendee", "office_id", string="Attendees", domain=[("state", "!=", "offline")]
    )
    guest_pass_ids = fields.One2many("virtual.guest.pass", "office_id", string="Guest Passes")

    floor_width = fields.Float("Floor width (m)", default=24.0)
    floor_depth = fields.Float("Floor depth (m)", default=18.0)
    theme = fields.Selection(
        [("light", "Light"), ("dark", "Dark"), ("brand", "Brand")], default="light"
    )
    brand_color = fields.Char(default="#7C4DFF")

    member_count = fields.Integer(compute="_compute_counts")
    room_count = fields.Integer(compute="_compute_counts")
    online_count = fields.Integer(compute="_compute_counts")
    guest_count = fields.Integer(compute="_compute_counts")

    join_url = fields.Char("Join link", compute="_compute_join_url")
    max_attendees = fields.Integer(
        "Max attendees", default=25, help="Soft cap on concurrent attendees in this office."
    )

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The office code/slug must be unique."),
        (
            "access_token_uniq",
            "unique(access_token)",
            "The public link token must be unique.",
        ),
    ]

    # ---------------------------------------------------------------- helpers
    @api.model
    def _default_access_token(self):
        return self.env["ir.config_parameter"].sudo().get_param("virtual_office.secret") or None

    def _generate_token(self):
        import secrets

        return secrets.token_urlsafe(24)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("access_token"):
                vals["access_token"] = self._generate_token()
            if not vals.get("code") and vals.get("name"):
                vals["code"] = self._slugify(vals["name"])
        offices = super().create(vals_list)
        if not self.env.context.get("virt_office_skip_lobby"):
            for office in offices.filtered(lambda o: not o.room_ids):
                office._ensure_lobby()
        return offices

    @api.model
    def _slugify(self, text):
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
        return slug or "office"

    def _ensure_lobby(self):
        """Every office needs at least one room to render and join."""
        self.ensure_one()
        if self.room_ids:
            return self.room_ids[0]
        return self.env["virtual.room"].create(
            {
                "name": "Lobby",
                "office_id": self.id,
                "room_type": "lounge",
                "capacity": max(self.max_attendees, 10),
                "pos_x": 0.0,
                "pos_y": 0.0,
                "width": 10.0,
                "depth": 8.0,
                "height": 3.2,
                "color": self.brand_color or "#7C4DFF",
            }
        )

    @api.depends("member_ids", "room_ids", "attendee_ids", "guest_pass_ids")
    def _compute_counts(self):
        for office in self:
            office.member_count = len(office.member_ids)
            office.room_count = len(office.room_ids)
            office.guest_count = len(office.guest_pass_ids)
            office.online_count = len(
                office.attendee_ids.filtered(lambda a: a.state != "offline")
            )

    def _compute_join_url(self):
        for office in self:
            office.join_url = office.get_join_url()

    # ------------------------------------------------------------------- urls
    def _base_url(self):
        return self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")

    def get_join_url(self):
        self.ensure_one()
        return "%s/virtual-office/%s" % (self._base_url(), self.access_token or self.id)

    def get_guest_base_url(self):
        self.ensure_one()
        return "%s/virtual-office/guest/" % self._base_url()

    # -------------------------------------------------------------- api (rpc)
    def action_open_office(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/virtual-office/office/%s" % self.id,
            "target": "self",
        }

    def get_layout(self):
        """Return a JSON-serialisable layout of the office for the 3D client."""
        self.ensure_one()
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "floor": {
                "width": self.floor_width,
                "depth": self.floor_depth,
                "theme": self.theme,
                "brand_color": self.brand_color,
            },
            "rooms": [r.get_room_data() for r in self.room_ids],
        }

    def save_layout(self, payload):
        """Persist a layout edited in the 3D client.

        ``payload`` carries an optional ``floor`` block and a ``rooms`` list.
        Only rooms belonging to this office are touched; unknown ids are
        ignored. Returns the fresh layout so the client can re-sync.
        """
        self.ensure_one()
        payload = payload or {}

        floor = payload.get("floor") or {}
        office_vals = {}
        if "floor_width" in floor and floor["floor_width"] is not None:
            office_vals["floor_width"] = max(4.0, float(floor["floor_width"]))
        if "floor_depth" in floor and floor["floor_depth"] is not None:
            office_vals["floor_depth"] = max(4.0, float(floor["floor_depth"]))
        if floor.get("theme") in dict(self._fields["theme"].selection):
            office_vals["theme"] = floor["theme"]
        if floor.get("brand_color"):
            office_vals["brand_color"] = str(floor["brand_color"])[:32]
        if office_vals:
            self.write(office_vals)

        valid_types = dict(self.env["virtual.room"]._fields["room_type"].selection)
        by_id = {r.id: r for r in self.room_ids}
        for item in payload.get("rooms") or []:
            try:
                rid = int(item.get("id") or 0)
            except (TypeError, ValueError):
                rid = 0
            vals = {}
            for key in ("pos_x", "pos_y", "rotation_y"):
                if item.get(key) is not None:
                    vals[key] = float(item[key])
            if item.get("width") is not None:
                vals["width"] = max(1.0, float(item["width"]))
            if item.get("depth") is not None:
                vals["depth"] = max(1.0, float(item["depth"]))
            if item.get("height") is not None:
                vals["height"] = max(0.5, float(item["height"]))
            if item.get("color"):
                vals["color"] = str(item["color"])[:32]
            if item.get("name"):
                vals["name"] = str(item["name"])[:128]
            if item.get("room_type") in valid_types:
                vals["room_type"] = item["room_type"]
            if item.get("capacity") is not None:
                vals["capacity"] = max(0, int(item["capacity"]))
            if "is_private" in item:
                vals["is_private"] = bool(item["is_private"])

            if rid:
                room = by_id.get(rid)
                if not room:
                    continue  # an id we do not own — ignore
                if vals:
                    room.write(vals)
            else:
                # No id → a room added in the editor; create it.
                vals.setdefault("name", "New Room")
                vals["office_id"] = self.id
                self.env["virtual.room"].create(vals)

        # Rooms removed in the editor (only ones this office owns).
        deleted = payload.get("deleted_room_ids") or []
        if deleted:
            ids = []
            for d in deleted:
                try:
                    ids.append(int(d))
                except (TypeError, ValueError):
                    continue
            if ids:
                victims = self.env["virtual.room"].search(
                    [("id", "in", ids), ("office_id", "=", self.id)]
                )
                if victims:
                    victims.unlink()
        return self.get_layout()
