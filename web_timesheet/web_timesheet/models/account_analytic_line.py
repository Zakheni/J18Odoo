# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticLineInherit(models.Model):
    _inherit = "account.analytic.line"

    expenditure_type = fields.Selection([
        ('normal', 'Normal'),
        ('overtime', 'Overtime'),
        ('weekend_overtime', 'Weekend overtime'),
        ('public_holiday_overtime', 'Public Holiday overtime'),
    ], string='Expenditure Type', default='normal')

    portal_user_id = fields.Many2one("res.users")
    ts_company_id = fields.Selection([('ztq_solutions','ZTQ Solutions'),
                                       ('zakheni_ict','Zakheni ICT'),
                                       ('zakhinfo_solutions','Zakinfo Solutions')], string='Organisation',
                                     related='project_id.ts_company_id'
                                     )


class ProjectInherit(models.Model):
    _inherit = "project.project"

    ts_company_id = fields.Selection([('ztq_solutions', 'ZTQ Solutions'),
                                      ('zakheni_ict', 'Zakheni ICT'),
                                      ('zakhinfo_solutions', 'Zakinfo Solutions')], string='Organisation')


 