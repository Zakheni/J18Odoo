from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    user_type = fields.Selection(
        [("employee", "Employee"), ("learner", "Learner")],
        string="User Type",
        default="employee",
        help="Defines the type of user. Learners are training programme participants "
        "with limited system access.",
    )
