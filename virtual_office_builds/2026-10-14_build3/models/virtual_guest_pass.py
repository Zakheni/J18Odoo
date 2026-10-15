import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VirtualGuestPass(models.Model):
    _name = "virtual.guest.pass"
    _description = "Virtual Office Guest Pass"
    _order = "create_date desc"

    name = fields.Char("Guest name", required=True)
    email = fields.Char()
    office_id = fields.Many2one(
        "virtual.office", required=True, ondelete="cascade", index=True
    )
    room_id = fields.Many2one(
        "virtual.room",
        ondelete="set null",
        help="If set, the guest is dropped straight into this room.",
    )
    company_id = fields.Many2one(related="office_id.company_id", store=True)
    created_by = fields.Many2one("res.users", default=lambda self: self.env.user)

    token = fields.Char(
        default=lambda self: secrets.token_urlsafe(20), copy=False, index=True
    )
    valid_from = fields.Datetime(default=fields.Datetime.now)
    valid_to = fields.Datetime(
        default=lambda self: fields.Datetime.now() + timedelta(hours=8)
    )
    max_duration_minutes = fields.Integer(
        "Max session (min)", default=120, help="0 = unlimited"
    )
    max_uses = fields.Integer("Max joins", default=0, help="0 = unlimited")
    use_count = fields.Integer(default=0, readonly=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("expired", "Expired"),
            ("revoked", "Revoked"),
        ],
        default="active",
    )

    guest_url = fields.Char("Guest link", compute="_compute_guest_url")

    _sql_constraints = [
        (
            "token_uniq",
            "unique(token)",
            "The guest pass token must be unique.",
        )
    ]

    def get_guest_url(self):
        self.ensure_one()
        return "%s/virtual-office/guest/%s" % (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url", ""),
            self.token,
        )

    def _compute_guest_url(self):
        for guest in self:
            guest.guest_url = guest.get_guest_url()

    def _is_valid(self):
        self.ensure_one()
        if self.state in ("revoked", "expired"):
            return False
        now = fields.Datetime.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        if self.max_uses and self.use_count >= self.max_uses:
            return False
        return True

    @api.model
    def resolve(self, token):
        """Return a valid guest pass for a token, or empty."""
        guest = (
            self.sudo()
            .search([("token", "=", token)], limit=1)
            .exists()
        )
        if guest and guest._is_valid():
            return guest
        return self.browse()

    def register_use(self):
        for guest in self:
            guest.sudo().write({"use_count": guest.use_count + 1})
            if guest.max_uses and guest.use_count >= guest.max_uses:
                guest.sudo().write({"state": "expired"})

    def action_revoke(self):
        self.write({"state": "revoked"})

    def action_activate(self):
        self.write({"state": "active"})

    @api.constrains("valid_from", "valid_to")
    def _check_dates(self):
        for guest in self:
            if guest.valid_from and guest.valid_to and guest.valid_to < guest.valid_from:
                raise ValidationError("The end of validity must be after its start.")
