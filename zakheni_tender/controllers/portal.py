from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class TenderPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super()._prepare_home_portal_values()
        partner = request.env.user.partner_id
        tenders = request.env['tender.tender'].search([
            '|',
            ('issuer_id', 'child_of', partner.id),
            ('message_partner_ids', 'in', partner.id),
        ])
        values['tender_count'] = len(tenders)
        return values

    @http.route(['/my/tenders', '/my/tenders/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_tenders(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Tender = request.env['tender.tender']

        domain = [
            '|',
            ('issuer_id', 'child_of', partner.id),
            ('message_partner_ids', 'in', partner.id),
        ]

        searchbar_sortings = {
            'deadline': {'label': _('Deadline'), 'order': 'deadline_submission'},
            'name': {'label': _('Name'), 'order': 'name'},
            'value': {'label': _('Value'), 'order': 'tender_value desc'},
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
        }
        sortby = sortby or 'deadline'
        order = searchbar_sortings[sortby]['order']

        tender_count = Tender.search_count(domain)
        pager = portal_pager(
            url='/my/tenders',
            total=tender_count,
            page=page,
            step=self._items_per_page,
        )
        tenders = Tender.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        request.session['my_tenders_history'] = tenders.ids[:100]

        values.update({
            'tenders': tenders,
            'page_name': 'tender',
            'pager': pager,
            'default_url': '/my/tenders',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render('zakheni_tender.portal_my_tenders', values)

    @http.route(['/my/tender/<int:tender_id>'], type='http', auth='user', website=True)
    def portal_my_tender_detail(self, tender_id=None, **kw):
        tender = request.env['tender.tender'].browse(tender_id)
        return request.render('zakheni_tender.portal_tender_detail', {
            'tender': tender,
            'resources': request.env['tender.document.resource'].search([('tender_id', '=', tender.id)]),
        })

    @http.route(['/my/tender/<int:tender_id>/upload'], type='http', auth='user', methods=['POST'], website=True)
    def portal_tender_upload(self, tender_id=None, **kw):
        tender = request.env['tender.tender'].browse(tender_id)
        if request.httprequest.method == 'POST':
            resource_name = (kw.get('resource_name') or '').strip()
            resource = False
            if resource_name:
                resource = request.env['tender.document.resource'].search([
                    ('tender_id', '=', tender.id),
                    ('name', '=', resource_name),
                ], limit=1)
                if not resource:
                    resource = request.env['tender.document.resource'].create({
                        'name': resource_name,
                        'tender_id': tender.id,
                    })
            files = request.httprequest.files.getlist('upload_file')
            for f in files:
                if f.filename:
                    vals = {
                        'name': f.filename,
                        'datas': f.read(),
                        'tender_id': tender.id,
                    }
                    if resource:
                        vals['resource_id'] = resource.id
                    request.env['tender.document'].create(vals)
        return request.redirect('/my/tender/%s' % tender_id)
