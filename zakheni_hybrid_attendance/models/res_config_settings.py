from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    zakheni_late_grace_minutes = fields.Integer(
        string="Late Grace (minutes)",
        default=15,
        help="Employees checking in later than this many minutes past their "
             "scheduled start are flagged as late.")
    zakheni_auto_approve_daily = fields.Boolean(
        string="Auto-Approve Daily Records",
        default=False,
        help="When enabled, daily work records with no exceptions are automatically approved.")


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zakheni_late_grace_minutes = fields.Integer(
        string="Late Grace (minutes)",
        related='company_id.zakheni_late_grace_minutes',
        readonly=False,
        config_parameter='zakheni_hybrid_attendance.zakheni_late_grace_minutes')
    zakheni_auto_approve_daily = fields.Boolean(
        string="Auto-Approve Daily Records",
        related='company_id.zakheni_auto_approve_daily',
        readonly=False,
        config_parameter='zakheni_hybrid_attendance.zakheni_auto_approve_daily')
