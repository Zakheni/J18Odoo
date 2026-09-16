# Zakheni Hybrid Attendance

Hybrid workforce attendance for Zakheni ICT, built on top of the standard
`hr_attendance` module. Distinguishes Office / WFH / Client / Off-site work
locations, tracks **planned vs actual** attendance per day, flags exceptions
(late, wrong location, missing check-out), supports approvals, produces a
monthly **attendance register** (Excel export) and a **live dashboard**.

Works on Odoo 17 and Odoo 18 as a single codebase.

## Installation

1. Copy the `zakheni_hybrid_attendance` folder into an addons directory and
   append it to `addons_path` in your Odoo configuration, e.g.:

   ```
   addons_path = ...,C:\odoo18\custom-addons\zakheni_hybrid_attendance
   ```

2. Install the module:

   ```
   python odoo-bin -c odoo.conf -d <database> -i zakheni_hybrid_attendance
   ```

   Dependencies: `hr_attendance`, `hr_holidays`.

3. Grant the **Hybrid Attendance / Manager** group
   (`zakheni_hybrid_attendance.group_zakheni_attendance_manager`) to the users
   who manage attendance, dashboards and the register. Regular employees get
   read-only access; daily records are restricted to their owner unless the
   user is a manager.

## Setup

### 1. Work locations

Single screen: **Hybrid Attendance → Work Locations**. Each location has:

- **Name / Code** — e.g. `Johannesburg HQ`, `HQ`
- **Type** — Office, Home / WFH, Client Site, Other
- **GPS coordinates** (latitude/longitude) and **Detection Radius (km)** —
  used for automatic location detection on check-in.

The module ships four default locations (Office, Home, Client, Other); edit
the coordinates or add your own sites.

### 2. Work schedules with planned locations

Planned location comes from the employee's work schedule
(`resource.calendar.attendance`, i.e. the green lines in the employee form's
**Schedule**). Each schedule line has a new **Work Location** field:
set it to the site the employee is expected to be that day/time.

- An employee with no explicit line for a day falls back to their
  **Default Work Location** on the employee form.
- The employee form also has a **Work Arrangement** field
  (Office / Hybrid / Remote / Field / Off-site).

The schedule today → planned check-in/check-out times and planned location
are computed per local day (timezone-aware, handles week-type and
midnight-crossing shifts).

### 3. Check-in / check-out

The standard `hr_attendance` systray check-in/check-out is replaced by this
module's `/zakheni_attendance/check` route, which:

- Calls Odoo's normal attendance logic (`_attendance_action_change`).
- Records GPS latitude/longitude/accuracy when the browser supplies them.
- Auto-detects the **work location** by matching the GPS point against the
  configured location radius (closest match wins). Falls back to the IP
  address or manual selection.
- Snaps a daily record for today so planned vs actual is compared live.

The dashboard consumes the same route for one-click check-in from the
dashboard screen.

## What the system tracks

For every attendance (`hr.attendance`):

- `work_location_id` — actual location (auto-detected or manual).
- `planned_location_id`, `planned_check_in_utc`, `planned_check_out_utc` —
  from the work schedule for that employee's day.
- Late check-in (`is_late`, `late_minutes`) — late if after the scheduled
  start plus the **Late Grace** minutes (Settings → HR Attendance, default 15).
- Location mismatch when actual ≠ planned location.
- Exception summary (`is_exception`, `exception_text`) combining
  late / wrong location / missing check-out.
- Status (`state`): Draft → Approved / Refused / Corrected.

Daily work records (`zakheni.attendance.day`, one per employee per local day)
roll these up: day type (present / absent / leave / day off / unscheduled),
planned vs actual location, worked hours, exception flags, and an
approve/refuse workflow.

Two cron jobs keep daily records populated: a nightly build for the previous
day and a 30-minute snapshot for today's live comparison.

## Approvals

- **Daily records** (menu **Hybrid Attendance → Daily Work Records**):
  select rows and **Approve** / **Refuse**, or edit individually.
- **Attendances**: approve/refuse buttons on the attendance list and form.
- Settings → HR Attendance → **Auto-Approve Daily Records**: when enabled,
  daily records without exceptions can be auto-approved.

## Monthly attendance register (Excel)

**People** menu / register button from the dashboard, or directly via
`/zakheni_attendance/register_export?month=MM&year=YYYY`.

The export (`attendance_register_YYYY_MM.xlsx`) contains:

- **Summary** sheet: month, number of employees, number of working days.
- **Register** sheet: one row per employee; one column per day of the month
  with the status (`P` present, `A` absent, `L` leave, `O` day off,
  `U` unscheduled), plus total worked hours and exception counters.

## Dashboard

**Hybrid Attendance → Dashboard** (OWL widget, polled every 30 s):

- KPI cards: total employees, scheduled, present, absent, on leave, day off.
- Today's live attendances grouped by work location type.
- Exception tallies: late, location mismatch, missing check-out, pending
  draft exceptions.
- Check-in/check-out button (with geolocation) and register download.

## Settings

- **Late Grace (minutes)** — default 15.
- **Auto-Approve Daily Records**.

## Compatibility notes

- Single codebase for Odoo 17 and 18; uses Odoo 18-style views (`<list>`,
  no `attrs`).
- The standard kiosk mode of `hr_attendance` is unchanged — this module
  extends the attendance engine but does not replace the kiosk. To use the
  kiosk, keep using **HR Attendance → Kiosk Mode** as usual; kiosk check-ins
  get IP-based location detection through the same `hr.attendance` hooks.

## Known environment note

On this Windows dev box, `zakheni_tender`'s optional
`sentence-transformers`/torch import can fail at Odoo startup
(`c10.dll` DLL init, `OSError` not `ImportError`). The guard in
`zakheni_tender/models/{tender_company_profile,tender_feed}.py` was widened
to `(ImportError, OSError)` so Odoo boots without that optional AI feature;
install the VC++ redistributable (or `pip install sentence-transformers`) if
you want it enabled.