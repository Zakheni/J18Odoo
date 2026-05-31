from odoo import _, api, fields, models


class AccountFollowupPlan(models.Model):
    _name = 'zakheni.followup.plan'
    _description = 'Follow-up Plan'
    _order = 'sequence, id'

    name = fields.Char('Plan Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    level_ids = fields.One2many('zakheni.followup.level', 'plan_id', string='Levels')
    active = fields.Boolean('Active', default=True)


class AccountFollowupLevel(models.Model):
    _name = 'zakheni.followup.level'
    _description = 'Follow-up Level'
    _order = 'plan_id, days_offset, id'

    plan_id = fields.Many2one('zakheni.followup.plan', string='Plan', required=True, ondelete='cascade')
    name = fields.Char('Level Name', required=True, translate=True)
    days_offset = fields.Integer('Days After Due Date', required=True, default=0,
        help='Send this follow-up N days after the invoice due date. Negative = before due date.')
    sequence = fields.Integer('Sequence', default=10)
    email_template_id = fields.Many2one('mail.template', string='Email Template',
        domain="[('model', '=', 'account.move')]")
    send_email = fields.Boolean('Send Email', default=True)
    send_letter = fields.Boolean('Send Letter', default=False)
    manual_action = fields.Boolean('Requires Manual Action', default=False,
        help='If checked, this level will not be triggered automatically. The user must manually mark it as done.')
    note = fields.Text('Internal Note')
    active = fields.Boolean('Active', default=True)


class AccountMove(models.Model):
    _inherit = 'account.move'

    followup_level_id = fields.Many2one('zakheni.followup.level', string='Last Follow-up Level')
    followup_date = fields.Date('Last Follow-up Date')
    followup_plan_id = fields.Many2one('zakheni.followup.plan', related='partner_id.followup_plan_id', readonly=True,
        string='Follow-up Plan', store=True)
    in_followup = fields.Boolean('In Follow-up', compute='_compute_in_followup', store=True)

    @api.depends('followup_level_id', 'invoice_date_due', 'payment_state', 'state')
    def _compute_in_followup(self):
        for move in self:
            move.in_followup = bool(
                move.followup_level_id
                and move.state == 'posted'
                and move.payment_state not in ('paid', 'reversed', 'invoicing_legacy')
            )

    def action_send_followup(self):
        self.ensure_one()
        plan = self.partner_id.followup_plan_id
        if not plan:
            return
        levels = plan.level_ids.filtered(lambda l: l.active).sorted('days_offset')
        current_level = self.followup_level_id
        next_idx = 0
        if current_level:
            for i, l in enumerate(levels):
                if l == current_level:
                    next_idx = i + 1
                    break
        if next_idx >= len(levels):
            return
        next_level = levels[next_idx]
        self.followup_level_id = next_level
        self.followup_date = fields.Date.today()
        if next_level.send_email and next_level.email_template_id:
            next_level.email_template_id.send_mail(self.id)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    followup_plan_id = fields.Many2one('zakheni.followup.plan', string='Follow-up Plan')
    followup_responsible_id = fields.Many2one('res.users', string='Follow-up Responsible')
