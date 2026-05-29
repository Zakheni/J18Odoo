from odoo import fields, models, _
from odoo.osv.expression import OR


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

    def _timesheet_get_portal_domain(self):
        """Portal users see follower-based timesheets plus their own employee lines and portal submissions."""
        domain = super()._timesheet_get_portal_domain()
        if self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            return domain
        user = self.env.user
        employees = self.env['hr.employee'].sudo().search([
            '|',
            ('user_id', '=', user.id),
            ('work_contact_id', '=', user.partner_id.id),
        ])
        extra = [[('portal_user_id', '=', user.id)]]
        if employees:
            extra.append([('employee_id', 'in', employees.ids)])
        return OR([domain] + extra)


class ProjectInherit(models.Model):
    _inherit = "project.project"

    ts_company_id = fields.Selection([('ztq_solutions', 'ZTQ Solutions'),
                                      ('zakheni_ict', 'Zakheni ICT'),
                                      ('zakhinfo_solutions', 'Zakinfo Solutions')], string='Organisation')


 