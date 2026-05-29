import json
from odoo import models, fields, api, _

class JobSpec(models.Model):
    _name = 'job.spec'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Job Spec Name')
    date = fields.Date(string='Date')
    note = fields.Text(string='Notes')