from odoo import fields, models


class TenderCategory(models.Model):
    _name = 'tender.tender.category'
    _description = 'Tender Category'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    description = fields.Text(string='Description')
