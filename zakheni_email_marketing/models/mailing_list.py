from odoo import api, fields, models


class MailingList(models.Model):
    _inherit = 'mailing.list'

    description = fields.Text('Description')
    category = fields.Selection([
        ('customer', 'Customers'),
        ('lead', 'Leads'),
        ('partner', 'Partners'),
        ('newsletter', 'Newsletter Subscribers'),
        ('segment', 'Dynamic Segment'),
        ('other', 'Other'),
    ], string='Category', default='other')
    is_dynamic = fields.Boolean(
        'Dynamic List',
        help='Automatically updated based on a domain filter.')
    dynamic_domain = fields.Char(
        'Dynamic Domain',
        help='Domain expression for automatic list population.')
    dynamic_model = fields.Char(
        'Source Model', default='mailing.contact')
    last_sync = fields.Datetime('Last Synchronized')

    segment_ids = fields.Many2many(
        'marketing.segment', string='Segments')

    subscription_preference_ids = fields.One2many(
        'marketing.subscription.preference', 'list_id',
        string='Subscription Preferences')

    def action_sync_dynamic_list(self):
        for lst in self.filtered('is_dynamic'):
            try:
                domain = eval(lst.dynamic_domain) if lst.dynamic_domain else []
                model = lst.dynamic_model or 'mailing.contact'
                records = self.env[model].search(domain)
                existing = lst.contact_ids
                existing_emails = set(existing.mapped('email') or [])
                new_emails = set(records.mapped('email') if hasattr(records, 'email') else [])
                to_remove = existing_emails - new_emails
                to_add = new_emails - existing_emails
                if to_remove:
                    remove_contacts = existing.filtered(lambda c: c.email in to_remove)
                    lst.write({'contact_ids': [(3, c.id) for c in remove_contacts]})
                if to_add:
                    for email in to_add:
                        contact = self.env['mailing.contact'].search([('email', '=', email)], limit=1)
                        if contact:
                            lst.write({'contact_ids': [(4, contact.id)]})
                lst.last_sync = fields.Datetime.now()
            except Exception:
                pass
