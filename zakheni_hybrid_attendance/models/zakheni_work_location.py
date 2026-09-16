import math

from odoo import api, fields, models


class ZakheniWorkLocation(models.Model):
    _name = "zakheni.work.location"
    _description = "Work Location"
    _order = "name"

    name = fields.Char(string="Location Name", required=True)
    code = fields.Char(string="Code", required=True)
    location_type = fields.Selection([
        ('office', 'Office'),
        ('home', 'Home / WFH'),
        ('client', 'Client Site'),
        ('other', 'Other'),
    ], string="Location Type", required=True, default='office')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company', string="Company",
        default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string="Address")
    latitude = fields.Float(string="Latitude", digits=(10, 7),
        help="GPS latitude of this location, used to auto-detect the work location on check-in.")
    longitude = fields.Float(string="Longitude", digits=(10, 7),
        help="GPS longitude of this location, used to auto-detect the work location on check-in.")
    radius_km = fields.Float(string="Detection Radius (km)", default=1.0,
        help="Distance (in km) from the coordinates within which a check-in "
             "is matched to this location.")
    note = fields.Text(string="Notes")

    @api.model
    def detect(self, latitude=False, longitude=False):
        """Return the work location (or empty recordset) that matches a set of GPS
        coordinates. The closest location within its configured radius wins."""
        if not latitude or not longitude:
            return self.browse()
        candidates = self.search([
            ('active', '=', True),
            ('latitude', '!=', 0),
            ('longitude', '!=', 0),
        ])
        best = self.browse()
        best_distance = False
        for loc in candidates:
            distance = self._haversine_km(latitude, longitude, loc.latitude, loc.longitude)
            if distance <= loc.radius_km and (best_distance is False or distance < best_distance):
                best = loc
                best_distance = distance
        return best

    @api.model
    def _haversine_km(self, lat1, lon1, lat2, lon2):
        radius = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return radius * 2 * math.asin(math.sqrt(a))

    @api.depends('name', 'location_type')
    def _compute_display_name(self):
        for location in self:
            if location.location_type:
                type_label = dict(
                    location._fields['location_type'].selection
                ).get(location.location_type)
                location.display_name = f"{location.name} ({type_label})"
            else:
                location.display_name = location.name
