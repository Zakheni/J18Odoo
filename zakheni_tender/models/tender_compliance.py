from odoo import api, fields, models, _


class TenderComplianceChecklist(models.Model):
    _name = 'tender.compliance.checklist'
    _description = 'Compliance Checklist Template'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    active = fields.Boolean(default=True)
    category_ids = fields.Many2many('tender.tender.category', string='Categories',
                                     help='Tender categories this checklist applies to')
    line_ids = fields.One2many('tender.compliance.checklist.line', 'checklist_id', string='Requirements')
    description = fields.Text(string='Description')


class TenderComplianceChecklistLine(models.Model):
    _name = 'tender.compliance.checklist.line'
    _description = 'Compliance Requirement'
    _order = 'sequence, id'

    checklist_id = fields.Many2one('tender.compliance.checklist', string='Checklist', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Requirement', required=True)
    description = fields.Text(string='Details')
    required = fields.Boolean(string='Mandatory', default=True)
    document_required = fields.Boolean(string='Requires Document Upload')
    help_text = fields.Text(string='Guidance')


class TenderComplianceResult(models.Model):
    _name = 'tender.compliance.result'
    _description = 'Tender Compliance Result'
    _rec_name = 'tender_id'

    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    checklist_id = fields.Many2one('tender.compliance.checklist', string='Checklist', required=True)
    company_id = fields.Many2one('res.company', related='tender_id.company_id', store=True)
    line_ids = fields.One2many('tender.compliance.result.line', 'result_id', string='Results')
    total_items = fields.Integer(compute='_compute_stats', string='Total Items')
    completed_items = fields.Integer(compute='_compute_stats', string='Completed')
    compliance_percent = fields.Float(compute='_compute_stats', string='Compliance (%)')

    _sql_constraints = [
        ('unique_tender_checklist', 'UNIQUE(tender_id, checklist_id)', 'Checklist already applied to this tender'),
    ]

    @api.depends('line_ids', 'line_ids.is_compliant')
    def _compute_stats(self):
        for r in self:
            lines = r.line_ids
            r.total_items = len(lines)
            r.completed_items = len(lines.filtered(lambda l: l.is_compliant))
            r.compliance_percent = (r.completed_items / r.total_items * 100) if r.total_items else 0.0

    @api.model
    def create_from_checklist(self, tender, checklist):
        result = self.create({
            'tender_id': tender.id,
            'checklist_id': checklist.id,
        })
        for line in checklist.line_ids:
            self.env['tender.compliance.result.line'].create({
                'result_id': result.id,
                'requirement_id': line.id,
                'name': line.name,
                'description': line.description,
                'required': line.required,
                'document_required': line.document_required,
            })
        return result


class TenderComplianceResultLine(models.Model):
    _name = 'tender.compliance.result.line'
    _description = 'Compliance Result Line'
    _order = 'requirement_id'

    result_id = fields.Many2one('tender.compliance.result', string='Result', required=True, ondelete='cascade')
    requirement_id = fields.Many2one('tender.compliance.checklist.line', string='Requirement')
    name = fields.Char(string='Requirement', required=True)
    description = fields.Text(string='Details')
    required = fields.Boolean(string='Mandatory', default=True)
    document_required = fields.Boolean(string='Requires Document')
    is_compliant = fields.Boolean(string='Compliant', default=False)
    notes = fields.Text(string='Notes')
    attachment_ids = fields.Many2many('ir.attachment', string='Supporting Documents')
