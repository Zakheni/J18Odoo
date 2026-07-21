from odoo import api, fields, models


class ScoringRule(models.Model):
    _name = "crm.scoring.rule"
    _description = "Lead Scoring Rule"
    _rec_name = "name"
    _order = "sequence, id"

    name = fields.Char("Rule Name", required=True)
    active = fields.Boolean("Active", default=True)
    sequence = fields.Integer("Sequence", default=10)
    category = fields.Selection([
        ("demographic", "Demographic"),
        ("engagement", "Engagement"),
        ("behavioral", "Behavioral"),
        ("firmographic", "Firmographic"),
    ], string="Category", required=True, default="demographic")
    score = fields.Integer("Score Value", required=True, default=5)
    apply_on = fields.Selection([
        ("country", "Country"),
        ("industry", "Industry"),
        ("email_domain", "Email Domain"),
        ("has_mobile", "Has Mobile Phone"),
        ("has_website", "Has Website"),
        ("revenue_range", "Expected Revenue Range"),
        ("city", "City"),
        ("state", "State"),
    ], string="Apply On", required=True)
    operator = fields.Selection([
        ("=", "Equals"),
        ("!=", "Not Equals"),
        ("like", "Contains"),
        (">", "Greater Than"),
        ("<", "Less Than"),
        (">=", "Greater or Equal"),
        ("<=", "Less or Equal"),
    ], string="Operator", default="=")
    value = fields.Char("Value", required=True)
    description = fields.Text("Description")

    def _evaluate(self, lead):
        self.ensure_one()
        field_map = {
            "country": "country_id.code" if lead.country_id else False,
            "industry": lead.industry_id.name if lead.industry_id else False,
            "email_domain": lead.email_from.split("@")[1] if lead.email_from and "@" in lead.email_from else False,
            "has_mobile": bool(lead.mobile),
            "has_website": bool(lead.website),
            "revenue_range": lead.expected_revenue,
            "city": lead.city,
            "state": lead.state_id.name if lead.state_id else False,
        }
        field_value = field_map.get(self.apply_on)
        if field_value is False:
            return 0
        try:
            if self.operator == "=":
                return self.score if str(field_value).lower() == str(self.value).lower() else 0
            elif self.operator == "!=":
                return self.score if str(field_value).lower() != str(self.value).lower() else 0
            elif self.operator == "like":
                return self.score if str(self.value).lower() in str(field_value).lower() else 0
            elif self.operator == ">":
                return self.score if float(field_value) > float(self.value) else 0
            elif self.operator == "<":
                return self.score if float(field_value) < float(self.value) else 0
            elif self.operator == ">=":
                return self.score if float(field_value) >= float(self.value) else 0
            elif self.operator == "<=":
                return self.score if float(field_value) <= float(self.value) else 0
        except (ValueError, TypeError):
            return 0
        return 0
