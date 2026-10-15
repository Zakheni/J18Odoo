# Virtual Office (Odoo 18)

A Katmai-style browser-based 3D virtual office for remote and hybrid teams:
a persistent 3D workspace you walk around, where you see who is around, walk
up to colleagues and talk instantly — real webcam video rendered as panels in
the 3D space, with positional (spatial) audio so you only hear people near you.

This module is the **control plane**. It owns everything server-side:

- **Offices** — one per company/team, with floor layout, theme, brand colour,
  capacity and a public/private switch.
- **Rooms** — positioned on the floor (X/Y, width/depth), typed (lounge,
  open space, conference, pod, phone booth), with capacity and optional
  private access lists.
- **Presence** — live attendees with position, room, camera/mic state, and a
  heartbeat that reaps stale sessions (45 s timeout, 1-minute cron).
- **Attendance integration** — entering an office auto-checks the user in
  (`hr.attendance`); leaving (or being reaped) checks them out. Per-office
  toggle (`attendance_enabled`). With `zakheni_hybrid_attendance` installed,
  check-ins map to a per-office `zakheni.work.location` (type "Home / WFH") so
  the hybrid dashboard sees virtual-office work as remote.
- **Device-presence monitoring** — the client reports `online` / `idle` (tab
  hidden) / `away` (no mouse/keyboard activity for 5 min) on every heartbeat.
  Combined with heartbeat staleness this drives a `device_status`
  (present / idle / away / gone) and an `away_minutes` counter, shown as
  badges in the office UI and as columns/filters in the backend attendee list
  ("Away from device", "Clocked in but away").
- **Guest passes** — token links that drop an external person straight into
  the office (optionally into a specific room), with expiry, max uses and
  revoke.
- **Chat** — per-office history, system events ("X joined the office").
- **Signalling** — a polling queue (`virtual.signal`) that relays WebRTC
  offer/answer/ICE envelopes between peers. Polling works for guests and
  avoids Odoo bus channel security; see the SFU upgrade path below.

The 3D rendering, WebRTC media and spatial audio run **client-side** in the
browser (Three.js + WebRTC + Web Audio) and are served by this module.

## Install

```bash
# add this repo's parent to addons_path, then:
odoo-bin -d <db> -i virtual_office --without-demo=all
```

Requires `hr_attendance` (standard Odoo). `zakheni_hybrid_attendance` is
optional — if present, virtual-office check-ins get a work location.

The module auto-creates a demo office ("Headquarters") with five rooms and two
crons (reap stale attendees, purge stale signals).

## Attendance behaviour

- **Check-in**: a logged-in user with an employee record who enters an office
  (attendee session created) is checked in via `hr.attendance`. Guests and
  users without an employee are skipped. If the employee is already clocked in
  elsewhere (kiosk, another office) no overlapping attendance is created.
- **Check-out**: leaving the office or being reaped as stale closes the
  attendance that the session opened (never someone else's).
- **Per-office toggle**: uncheck "Auto clock-in/out" on the office form to
  disable it for that office.
- **Work location**: with `zakheni_hybrid_attendance` installed, each office
  maps to a `zakheni.work.location` (found or auto-created, type "Home / WFH")
  so the hybrid dashboard's location split and mismatch logic work.

## Device-presence monitoring

- The client sends `state` on every heartbeat: `online` (tab focused and
  active), `idle` (tab hidden), `away` (no mouse/keyboard/touch activity in
  the tab for 5 minutes).
- The backend derives `device_status` (present / idle / away / gone) from
  state + heartbeat staleness (45 s), and `away_minutes`.
- In the office UI, away people get a badge ("idle 12m", "away 3m", "gone").
- In the backend, the Attendees list shows Device status / Away (min) /
  Clocked in columns and filters: **Away from device** and **Clocked in but
  away**.

## Using it

- Logged-in users: `/virtual-office` (first open office) or
  `/virtual-office/office/<id>`.
- Guests: share the office's guest link (visible on the office form when the
  office is public). Guests land on `/virtual-office/guest/<token>`.
- The office form shows a copyable join URL and per-room occupancy.

## JSON API (all `auth="public"`, `csrf=False`, JSON body)

| Endpoint | Method | Purpose |
|---|---|---|
| `/virtual-office/api/join` | POST | Create an attendee session. Body: `office_id`, optional `room_id`, optional `guest_token`. Returns `token`, `peer_id`, `self`, `office` layout. |
| `/virtual-office/api/heartbeat` | POST | Keep-alive + state sync. Body: `token`, position/camera/mic/state, optional `room_id`, `since_chat_id`. Returns `peers` (same room), `everyone`, `rooms` occupancy, `signals`, `chat`. |
| `/virtual-office/api/leave` | POST | End the session (token becomes invalid). |
| `/virtual-office/api/signal` | POST | Push a WebRTC envelope. Body: `token`, `to` (peer_id), `kind`, `payload`. |
| `/virtual-office/api/chat/send` | POST | Post a chat message. Body: `token`, `body`, optional `room_id`. |
| `/virtual-office/api/chat/history` | POST | Fetch messages after `since_chat_id`. |
| `/virtual-office/api/guest/create` | POST | Create a guest pass (attendees only, office must be public). Body: `token`, `name`, `email`. Returns `url`. |
| `/virtual-office/api/state` | POST/GET | Full office snapshot. |

## Frontend

`static/src/js/`:

- `vo_api.js` — fetch wrapper for the JSON API.
- `vo_rtc.js` — WebRTC mesh; deterministic offerer (`selfPeer < peerId`) so
  peers don't both offer. Video tracks are attached to 3D panels.
- `vo_audio.js` — HRTF `PannerNode` spatial audio: volume/pan by distance and
  angle in the 3D scene.
- `vo_scene.js` — Three.js office: floor, rooms, avatars (webcam
  `VideoTexture`), click-to-move + WASD, room detection.
- `vo_ui.js` — HUD, chat panel, minimap, mute/camera toggles.
- `vo_main.js` — wiring + heartbeat loop (~900 ms; 180 ms when dirty).

Three.js r128 is vendored at `static/lib/three.min.js` for offline/intranet
use.

## Media transport: mesh today, SFU tomorrow

The current transport is a **peer-to-peer WebRTC mesh** — fine for small rooms
(2–8 people). For large rooms, swap it for an SFU:

1. Deploy an SFU (LiveKit, mediasoup, Janus) and give the client its URL.
2. Replace the `virtual.signal` polling relay with a WebSocket/DataChannel
   signalling path (or keep polling — it works for guests).
3. In `vo_rtc.js`, replace the mesh with SFU publish/subscribe; keep the
   spatial-audio mixing in `vo_audio.js` (SFUs can also do spatial audio
   server-side, e.g. LiveKit's spatial audio).

## Testing

The module was validated end-to-end against a scratch database:

- `py_compile` on all models/controllers, `node --check` on all JS.
- XML schema validation via Odoo's own RelaxNG on install.
- Live HTTP integration test (guest join ×2, heartbeat peer discovery,
  signal relay, chat, state, leave, stale-token rejection) — 15/15 checks.

## Odoo 18 notes

- List views use `<list>` (not `<tree>`); `attrs`/`states` are gone — use
  `invisible="expr"` directly; kanban cards use `t-name="card"`.
- `mail.activity.mixin` is required for `activity_ids` in the chatter.
- `&hellip;`-style HTML entities are invalid in XML data files — use
  `&#8230;` or literal characters.