import json
import logging
from datetime import timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Signals older than this are dropped (the peer clearly never polled).
SIGNAL_TTL_SECONDS = 60


class VirtualSignal(models.Model):
    """Short-lived WebRTC signalling envelopes relayed between two peers.

    The client polls `/virtual-office/api/heartbeat`, which drains the queue of
    signals addressed to its peer id. This keeps signalling working for guests
    (who cannot subscribe to arbitrary Odoo bus channels) without a second
    service. For very low latency, swap this for a dedicated WebSocket service -
    see README.md.
    """

    _name = "virtual.signal"
    _description = "Virtual Office WebRTC Signal"
    _order = "id"

    office_id = fields.Many2one("virtual.office", ondelete="cascade", index=True)
    from_peer = fields.Char(index=True)
    to_peer = fields.Char(index=True, required=True)
    kind = fields.Selection(
        [("offer", "offer"), ("answer", "answer"), ("candidate", "candidate"), ("bye", "bye")],
        required=True,
    )
    payload = fields.Text()
    create_date = fields.Datetime(readonly=True)

    @api.model
    def push(self, office, from_peer, to_peer, kind, payload):
        if kind not in ("offer", "answer", "candidate", "bye"):
            return self.browse()
        if isinstance(payload, (dict, list)):
            payload = json.dumps(payload)
        return self.sudo().create(
            {
                "office_id": office.id if office else False,
                "from_peer": from_peer,
                "to_peer": to_peer,
                "kind": kind,
                "payload": payload,
            }
        )

    @api.model
    def drain(self, to_peer):
        signals = self.sudo().search([("to_peer", "=", to_peer)])
        data = [
            {"from": s.from_peer, "kind": s.kind, "payload": s.payload}
            for s in signals
        ]
        signals.sudo().unlink()
        return data

    @api.model
    def _gc(self):
        limit = fields.Datetime.now() - timedelta(seconds=SIGNAL_TTL_SECONDS)
        old = self.sudo().search([("create_date", "<", limit)])
        count = len(old)
        old.sudo().unlink()
        if count:
            _logger.info("Virtual Office: purged %s stale signals", count)
        return count
