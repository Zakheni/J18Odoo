from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TenderStage(models.Model):
    _name = 'tender.stage'
    _description = 'Tender Stage'
    _order = 'sequence, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    fold = fields.Boolean(
        string='Folded in Kanban',
        help='This stage is folded in the Kanban view when there are no records in it.',
    )
    probability = fields.Float(
        string='Win Probability (%)',
        help='Default win probability when a tender reaches this stage.',
    )
    is_won = fields.Boolean(string='Won Stage')
    is_lost = fields.Boolean(string='Lost Stage')
