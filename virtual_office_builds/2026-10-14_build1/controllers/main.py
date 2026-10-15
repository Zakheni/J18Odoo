import json
import logging

from markupsafe import Markup

from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo import fields

_logger = logging.getLogger(__name__)


class VirtualOfficeController(http.Controller):
    # =====================================================================
    #  Page delivery (serves the 3D client)
    # =====================================================================
    @http.route("/virtual-office", type="http", auth="user", website=False)
    def virtual_office_home(self, **kw):
        office = (
            request.env["virtual.office"]
            .sudo()
            .search([("state", "=", "open")], limit=1)
        )
        if not office:
            return request.not_found()
        return self._render_office(office, is_guest=False)

    @http.route(
        "/virtual-office/office/<int:office_id>", type="http", auth="user", website=False
    )
    def virtual_office_office(self, office_id, **kw):
        office = request.env["virtual.office"].sudo().browse(office_id).exists()
        if not office or not office.active:
            return request.not_found()
        return self._render_office(office, is_guest=False)

    @http.route(
        "/virtual-office/token/<string:token>", type="http", auth="user", website=False
    )
    def virtual_office_token(self, token, **kw):
        office = (
            request.env["virtual.office"]
            .sudo()
            .search([("access_token", "=", token)], limit=1)
        )
        if not office:
            return request.not_found()
        return self._render_office(office, is_guest=False)

    @http.route(
        "/virtual-office/guest/<string:token>", type="http", auth="public", website=False
    )
    def virtual_office_guest(self, token, **kw):
        guest = request.env["virtual.guest.pass"].resolve(token)
        if not guest:
            return request.render(
                "virtual_office.guest_invalid_page", {}
            )
        return self._render_office(guest.office_id, is_guest=True, guest=guest)

    def _render_office(self, office, is_guest=False, guest=None):
        office = office.sudo()
        if not office.room_ids:
            office._ensure_lobby()
        boot = {
            "office": office.get_layout(),
            "api": "/virtual-office/api",
            "isGuest": is_guest,
            "userName": request.env.user.name if not is_guest else (guest.name if guest else "Guest"),
            "makerName": office.manager_id.name or "",
            "guestToken": guest.token if guest else False,
            "joinUrl": office.get_join_url(),
            "guestUrlBase": office.get_guest_base_url(),
            "isPublic": office.is_public,
            "officeId": office.id,
        }
        return request.render(
            "virtual_office.office_page",
            {
                "bootstrap": Markup(
                    json.dumps(boot).replace("</", "<\\/")
                ),
                "office": office,
            },
        )

    # =====================================================================
    #  JSON API
    # =====================================================================
    def _json_response(self, data, status=200):
        return request.make_json_response(data, status=status)

    def _body(self):
        try:
            raw = request.httprequest.get_data(as_text=True) or "{}"
            return json.loads(raw)
        except Exception:
            return {}

    def _attendee(self, token):
        return request.env["virtual.attendee"].authenticate(token)

    def _require(self, token):
        att = self._attendee(token)
        if not att:
            raise AccessError("Invalid or expired session. Please rejoin.")
        return att

    def _can_enter(self, office, user):
        if user.has_group("virtual_office.group_virtual_office_manager"):
            return True
        if user.has_group("base.group_system"):
            return True
        if office.is_public:
            return True
        return user in office.member_ids

    # ---------------------------------------------------------------- join
    @http.route(
        "/virtual-office/api/join", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_join(self, **kw):
        try:
            data = self._body()
            office = (
                request.env["virtual.office"]
                .sudo()
                .browse(int(data.get("office_id") or 0))
                .exists()
            )
            if not office or office.state != "open":
                return self._json_response({"ok": False, "error": "Office not available."}, 404)

            user = request.env.user
            guest = None
            guest_token = data.get("guest_token")
            if guest_token:
                guest = request.env["virtual.guest.pass"].resolve(guest_token)
                if not guest or guest.office_id != office:
                    return self._json_response({"ok": False, "error": "Guest pass invalid."}, 403)
            else:
                if user._is_public() or not self._can_enter(office, user):
                    return self._json_response({"ok": False, "error": "Not allowed."}, 403)

            online = len(
                office.attendee_ids.filtered(lambda a: a.state != "offline")
            )
            if online >= office.max_attendees:
                return self._json_response({"ok": False, "error": "Office is full."}, 409)

            room = None
            room_id = data.get("room_id")
            if room_id:
                room = request.env["virtual.room"].sudo().browse(int(room_id)).exists()
                if room and room.office_id != office:
                    room = None
            if room is None and guest and guest.room_id:
                room = guest.room_id

            att = request.env["virtual.attendee"].join(
                office, room=room, user=user if not guest else None, guest_pass=guest
            )
            if guest:
                guest.register_use()
            # Announce arrival.
            request.env["virtual.chat.message"].post(
                office,
                "%s joined the office" % att.name,
                room=att.room_id,
                system=True,
            )
            return self._json_response({
                "ok": True,
                "token": att.access_token,
                "peer_id": att.peer_id,
                "self": att.get_public_data(),
                "office": office.get_layout(),
                "room_id": att.room_id.id if att.room_id else False,
            })
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office join failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)

    # ----------------------------------------------------------- heartbeat
    @http.route(
        "/virtual-office/api/heartbeat", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_heartbeat(self, **kw):
        try:
            data = self._body()
            att = self._require(data.get("token"))
            att.heartbeat(data)

            office = att.office_id
            # peers = online attendees in the same room, excluding me
            peers = office.attendee_ids.filtered(
                lambda a: a.state != "offline"
                and a.id != att.id
                and a.room_id == att.room_id
            )
            everyone = office.attendee_ids.filtered(lambda a: a.state != "offline")

            signals = request.env["virtual.signal"].drain(att.peer_id)

            since_id = int(data.get("since_chat_id") or 0)
            domain = [("office_id", "=", office.id), ("id", ">", since_id)]
            messages = (
                request.env["virtual.chat.message"]
                .sudo()
                .search(domain, order="id", limit=50)
            )

            return self._json_response({
                "ok": True,
                "self": att.get_public_data(),
                "room_id": att.room_id.id if att.room_id else False,
                "peers": [p.get_public_data() for p in peers],
                "rooms": [
                    {"id": r.id, "name": r.name, "occupancy": r.occupancy}
                    for r in office.room_ids
                ],
                "everyone": [
                    {
                        "peer_id": a.peer_id,
                        "name": a.name,
                        "room_id": a.room_id.id if a.room_id else False,
                        "state": a.state,
                        "is_guest": a.is_guest,
                        "position": {"x": a.pos_x, "y": a.pos_y},
                        "camera_on": a.camera_on,
                        "mic_on": a.mic_on,
                    }
                    for a in everyone
                ],
                "signals": signals,
                "chat": [m.get_chat_data() for m in messages],
            })
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office heartbeat failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)

    # --------------------------------------------------------------- leave
    @http.route(
        "/virtual-office/api/leave", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_leave(self, **kw):
        data = self._body()
        att = self._attendee(data.get("token"))
        if att:
            att.leave()
        return self._json_response({"ok": True})

    # -------------------------------------------------------------- signal
    @http.route(
        "/virtual-office/api/signal", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_signal(self, **kw):
        try:
            data = self._body()
            att = self._require(data.get("token"))
            to_peer = data.get("to")
            if to_peer and to_peer != att.peer_id:
                request.env["virtual.signal"].push(
                    att.office_id, att.peer_id, to_peer, data.get("kind"), data.get("payload")
                )
            return self._json_response({"ok": True})
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office signal failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)

    # ---------------------------------------------------------------- chat
    @http.route(
        "/virtual-office/api/chat/send", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_chat_send(self, **kw):
        try:
            data = self._body()
            att = self._require(data.get("token"))
            body = (data.get("body") or "").strip()
            if not body:
                return self._json_response({"ok": False, "error": "Empty message."}, 400)
            room = None
            room_id = data.get("room_id")
            if room_id:
                room = request.env["virtual.room"].sudo().browse(int(room_id)).exists()
                if room and room.office_id != att.office_id:
                    room = None
            msg = request.env["virtual.chat.message"].post(
                att.office_id,
                body[:4000],
                room=room,
                author=att.user_id or None,
                guest_pass=att.guest_pass_id or None,
                peer_id=att.peer_id,
            )
            return self._json_response({"ok": True, "message": msg.get_chat_data()})
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office chat send failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)

    @http.route(
        "/virtual-office/api/chat/history", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_chat_history(self, **kw):
        try:
            data = self._body()
            att = self._require(data.get("token"))
            since_id = int(data.get("since_chat_id") or 0)
            messages = (
                request.env["virtual.chat.message"]
                .sudo()
                .search(
                    [("office_id", "=", att.office_id.id), ("id", ">", since_id)],
                    order="id",
                    limit=100,
                )
            )
            return self._json_response(
                {"ok": True, "chat": [m.get_chat_data() for m in messages]}
            )
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office chat history failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)

    # ------------------------------------------------------- guest invite
    @http.route(
        "/virtual-office/api/guest/create", type="http", auth="public", methods=["POST"],
        csrf=False, website=False,
    )
    def api_guest_create(self, **kw):
        try:
            data = self._body()
            att = self._require(data.get("token"))
            if att.is_guest:
                return self._json_response({"ok": False, "error": "Guests cannot invite."}, 403)
            office = att.office_id
            if not office.is_public:
                return self._json_response(
                    {"ok": False, "error": "Guest links are disabled for this office."}, 403
                )
            guest = request.env["virtual.guest.pass"].sudo().create({
                "name": (data.get("name") or "Guest").strip()[:64],
                "email": (data.get("email") or "").strip()[:128],
                "office_id": office.id,
            })
            return self._json_response({"ok": True, "url": guest.get_guest_url(), "id": guest.id})
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office guest create failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)

    # --------------------------------------------------------------- state
    @http.route(
        "/virtual-office/api/state", type="http", auth="public", methods=["POST", "GET"],
        csrf=False, website=False,
    )
    def api_state(self, **kw):
        try:
            data = self._body()
            token = data.get("token") or request.httprequest.args.get("token")
            att = self._require(token)
            office = att.office_id
            everyone = office.attendee_ids.filtered(lambda a: a.state != "offline")
            return self._json_response({
                "ok": True,
                "office": office.get_layout(),
                "self": att.get_public_data(),
                "everyone": [
                    {
                        "peer_id": a.peer_id,
                        "name": a.name,
                        "room_id": a.room_id.id if a.room_id else False,
                        "state": a.state,
                        "is_guest": a.is_guest,
                        "position": {"x": a.pos_x, "y": a.pos_y},
                        "camera_on": a.camera_on,
                        "mic_on": a.mic_on,
                    }
                    for a in everyone
                ],
            })
        except AccessError as e:
            return self._json_response({"ok": False, "error": str(e)}, 403)
        except Exception as e:  # noqa: BLE001
            _logger.exception("virtual_office state failed")
            return self._json_response({"ok": False, "error": str(e)}, 500)
