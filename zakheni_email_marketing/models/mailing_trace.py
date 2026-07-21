from odoo import api, fields, models


class MailingTrace(models.Model):
    _inherit = 'mailing.trace'

    zakheni_conversion_date = fields.Datetime('Conversion Date')
    zakheni_conversion_amount = fields.Float(
        'Conversion Amount')
    zakheni_conversion_model = fields.Char('Conversion Model')
    zakheni_conversion_res_id = fields.Integer('Conversion Record ID')

    ip_address = fields.Char('IP Address')
    user_agent = fields.Char('User Agent')
    device_type = fields.Selection([
        ('desktop', 'Desktop'),
        ('mobile', 'Mobile'),
        ('tablet', 'Tablet'),
    ], string='Device Type')
    country_id = fields.Many2one('res.country', string='Country')
    city = fields.Char('City')

    def register_conversion(self, amount=0.0, model=None, res_id=None):
        self.ensure_one()
        self.write({
            'zakheni_conversion_date': fields.Datetime.now(),
            'zakheni_conversion_amount': amount,
            'zakheni_conversion_model': model,
            'zakheni_conversion_res_id': res_id,
        })
        if self.contact_id:
            self.contact_id.total_conversions += 1
            self.contact_id.last_conversion_date = fields.Datetime.now()
