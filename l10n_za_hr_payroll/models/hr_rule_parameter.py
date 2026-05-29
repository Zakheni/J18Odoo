from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrRuleParameter(models.Model):
    _name = "hr.rule.parameter"
    _description = "Salary Rule Parameter"
    _rec_name = "code"
    _order = "code, date_from desc"

    code = fields.Char(required=True, index=True)
    name = fields.Char(required=True, translate=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date()
    value = fields.Float(required=True, digits="Payroll")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    _sql_constraints = [
        (
            "unique_code_date",
            "unique(code, date_from, company_id)",
            "A parameter with the same code and date already exists for this company.",
        ),
    ]

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_to and rec.date_from > rec.date_to:
                raise ValidationError(_("Date from must be before date to."))

    @api.model
    def get_parameter(self, code, date=None, company_id=None):
        if not date:
            date = fields.Date.today()
        if not company_id:
            company_id = self.env.company.id
        domain = [
            ("code", "=", code),
            ("date_from", "<=", date),
            ("company_id", "=", company_id),
        ]
        param = self.search(domain, order="date_from desc", limit=1)
        if not param:
            param = self.search(
                [("code", "=", code), ("company_id", "=", company_id)],
                order="date_from desc",
                limit=1,
            )
        if param:
            return param[0].value
        return 0.0


class HrRuleParameterBracket(models.Model):
    _name = "hr.rule.parameter.bracket"
    _description = "Tax Bracket"
    _order = "parameter_id, sequence"

    parameter_id = fields.Many2one(
        "hr.rule.parameter", string="Parameter", required=True, ondelete="cascade"
    )
    sequence = fields.Integer(default=10)
    from_amount = fields.Float(required=True, digits="Payroll")
    to_amount = fields.Float(digits="Payroll")
    rate = fields.Float(required=True, digits="Payroll Rate", string="Rate (%)")
    base_amount = fields.Float(
        string="Base Amount",
        digits="Payroll",
        help="Fixed base tax amount for this bracket",
    )

    @api.model
    def get_brackets(self, parameter_code, date=None, company_id=None):
        param_model = self.env["hr.rule.parameter"]
        param_value = param_model.get_parameter(parameter_code, date, company_id)
        param = param_model.search(
            [("code", "=", parameter_code), ("value", "=", param_value)], limit=1
        )
        if param:
            return self.search(
                [("parameter_id", "=", param.id)], order="sequence"
            )
        return self.env["hr.rule.parameter.bracket"]
