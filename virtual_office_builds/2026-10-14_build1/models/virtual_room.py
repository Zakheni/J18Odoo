from odoo import api, fields, models


class VirtualRoom(models.Model):
    _name = "virtual.room"
    _description = "Virtual Office Room"
    _order = "office_id, sequence, name"

    name = fields.Char(required=True)
    office_id = fields.Many2one(
        "virtual.office", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(related="office_id.company_id", store=True)
    sequence = fields.Integer(default=10)
    room_type = fields.Selection(
        [
            ("reception", "Reception"),
            ("open_space", "Open Space"),
            ("office", "Private Office"),
            ("pod", "Co-working Pod"),
            ("conference", "Conference Room"),
            ("lounge", "Lounge"),
            ("phone_booth", "Phone Booth"),
        ],
        default="open_space",
        required=True,
    )
    description = fields.Char()
    capacity = fields.Integer(default=8)

    # --- geometry on the floor plan (metres, centre-anchored) ---
    pos_x = fields.Float("X position", default=0.0)
    pos_y = fields.Float("Y position", default=0.0)
    width = fields.Float(default=6.0)
    depth = fields.Float(default=6.0)
    height = fields.Float(default=3.0)
    rotation_y = fields.Float("Rotation (rad)", default=0.0)
    color = fields.Char(default="#4A90D9")

    # --- access ---
    is_private = fields.Boolean(string="Private room")
    allowed_user_ids = fields.Many2many(
        "res.users",
        "virtual_room_user_rel",
        "room_id",
        "user_id",
        string="Allowed users",
        help="If private, only these users (plus office managers) may enter.",
    )

    attendee_ids = fields.One2many("virtual.attendee", "room_id", string="Attendees")
    occupancy = fields.Integer(compute="_compute_occupancy", store=False)

    def _compute_occupancy(self):
        for room in self:
            room.occupancy = len(room.attendee_ids.filtered(lambda a: a.state != "offline"))

    def get_room_data(self):
        self.ensure_one()
        return {
            "id": self.id,
            "name": self.name,
            "type": self.room_type,
            "capacity": self.capacity,
            "private": self.is_private,
            "position": {"x": self.pos_x, "y": self.pos_y, "z": 0.0},
            "size": {"w": self.width, "d": self.depth, "h": self.height},
            "rotation_y": self.rotation_y,
            "color": self.color,
        }
