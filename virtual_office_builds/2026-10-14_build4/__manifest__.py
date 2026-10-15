{
    "name": "Virtual Office",
    "version": "18.0.1.5.0",
    "summary": "Katmai-style 3D virtual office: presence, live video, spatial audio, chat and guest links",
    "description": """
        Virtual Office
        ==============

        A browser-based 3D workspace for remote and hybrid teams, in the spirit
        of Katmai: a persistent 3D office you walk around, where you see who is
        around, walk up to colleagues and talk instantly - real webcam video
        rendered as panels in the 3D space, with positional (spatial) audio so
        you only hear people near you.

        This module is the control plane: it owns offices, rooms, presence,
        guest passes, chat history and the HTTP/WebRTC signalling API. The 3D
        rendering, WebRTC media and spatial audio run client-side in the browser
        (Three.js + WebRTC + Web Audio) and are served by this module.

        Media transport is a peer-to-peer WebRTC mesh, which is ideal for small
        rooms. For large rooms, swap the transport for an SFU (LiveKit,
        mediasoup, Janus) - see README.md for the upgrade path.
    """,
    "author": "Jermaine / Zakheni ICT",
    "website": "https://zakheni.co.za",
    "category": "Productivity",
    "license": "LGPL-3",
    "depends": ["base", "mail", "hr_attendance"],
    "external_dependencies": {"python": []},
    "data": [
        "security/virtual_office_security.xml",
        "security/ir.model.access.csv",
        "security/virtual_office_rules.xml",
        "data/virtual_office_data.xml",
        "views/virtual_office_actions.xml",
        "views/virtual_office_views.xml",
        "views/virtual_room_views.xml",
        "views/virtual_attendee_views.xml",
        "views/virtual_guest_pass_views.xml",
        "views/virtual_chat_views.xml",
        "views/virtual_office_templates.xml",
        "views/virtual_office_menus.xml",
    ],
    "demo": [
        "demo/virtual_office_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
