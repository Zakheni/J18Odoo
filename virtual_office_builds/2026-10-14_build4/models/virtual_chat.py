from odoo import api, fields, models


class VirtualChatMessage(models.Model):
    _name = "virtual.chat.message"
    _description = "Virtual Office Chat Message"
    _order = "id"

    office_id = fields.Many2one(
        "virtual.office", required=True, ondelete="cascade", index=True
    )
    room_id = fields.Many2one(
        "virtual.room",
        ondelete="set null",
        help="Scope the message to a room; empty means office-wide.",
    )
    company_id = fields.Many2one(related="office_id.company_id", store=True)

    author_id = fields.Many2one("res.users", ondelete="set null")
    author_name = fields.Char()
    author_peer_id = fields.Char()
    is_guest = fields.Boolean()
    is_system = fields.Boolean()

    body = fields.Text(required=True)

    @api.model
    def post(self, office, body, room=None, author=None, guest_pass=None, peer_id=None, system=False):
        vals = {
            "office_id": office.id,
            "room_id": room.id if room else False,
            "body": body,
            "author_peer_id": peer_id,
            "is_system": system,
        }
        if guest_pass:
            vals["is_guest"] = True
            vals["author_name"] = guest_pass.name
        elif author and not author._is_public():
            vals["author_id"] = author.id
            vals["author_name"] = author.name
        else:
            vals["author_name"] = "Guest"
        return self.sudo().create(vals)

    def get_chat_data(self):
        self.ensure_one()
        return {
            "id": self.id,
            "body": self.body,
            "author": self.author_name or "System",
            "author_peer_id": self.author_peer_id,
            "is_guest": self.is_guest,
            "is_system": self.is_system,
            "room_id": self.room_id.id if self.room_id else False,
            "date": fields.Datetime.to_string(self.create_date),
        }
