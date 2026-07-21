from odoo import http, fields
from odoo.http import request


class AssetScanController(http.Controller):

    @http.route('/asset/scan/<barcode>', type='http', auth='user')
    def asset_scan(self, barcode, **kwargs):
        asset = request.env['asset.asset'].search([('barcode', '=', barcode)], limit=1)
        if not asset:
            return request.not_found()

        user = request.env.user
        employee = user.employee_id
        active = request.env['asset.assignment'].search([
            ('asset_id', '=', asset.id),
            ('state', '=', 'assigned'),
        ], limit=1, order='assigned_date desc')
        return request.render('zakheni_asset_management.asset_scan_it_choice', {
            'asset': asset,
            'employee': employee,
            'active_assignment': active,
            'is_it_support': user.has_group('zakheni_asset_management.group_asset_it_support'),
        })

    @http.route('/asset/scan/<barcode>/assign', type='http', auth='user')
    def asset_scan_assign(self, barcode, **kwargs):
        asset = request.env['asset.asset'].search([('barcode', '=', barcode)], limit=1)
        if not asset:
            return request.not_found()

        user = request.env.user
        employee = user.employee_id
        if not employee:
            return request.render('zakheni_asset_management.asset_scan_message', {
                'title': 'No Employee Record',
                'message': 'Your user account is not linked to an employee record.',
            })

        existing = request.env['asset.assignment'].search([
            ('asset_id', '=', asset.id),
            ('state', '=', 'assigned'),
        ], limit=1)
        if existing:
            return request.render('zakheni_asset_management.asset_scan_message', {
                'title': 'Already Assigned',
                'message': f'Asset {asset.display_name} is already assigned to {existing.employee_id.name}. Return it first.',
            })

        assignment = request.env['asset.assignment'].create({
            'asset_id': asset.id,
            'employee_id': employee.id,
            'assigned_date': fields.Date.today(),
            'state': 'assigned',
        })
        asset.write({'status': 'in_use'})

        return request.render('zakheni_asset_management.asset_scan_assigned', {
            'asset': asset,
            'assignment': assignment,
        })

    @http.route('/asset/scan/<barcode>/return', type='http', auth='user')
    def asset_scan_return(self, barcode, **kwargs):
        asset = request.env['asset.asset'].search([('barcode', '=', barcode)], limit=1)
        if not asset:
            return request.not_found()

        active = request.env['asset.assignment'].search([
            ('asset_id', '=', asset.id),
            ('state', '=', 'assigned'),
        ], limit=1, order='assigned_date desc')
        if active:
            active.action_return()

        asset.write({'status': 'in_storage'})

        return request.render('zakheni_asset_management.asset_scan_returned', {
            'asset': asset,
            'assignment': active or request.env['asset.assignment'],
        })

    @http.route('/asset/scan/<barcode>/mark_not_in_use', type='http', auth='user')
    def asset_scan_mark_not_in_use(self, barcode, **kwargs):
        asset = request.env['asset.asset'].search([('barcode', '=', barcode)], limit=1)
        if not asset:
            return request.not_found()

        active = request.env['asset.assignment'].search([
            ('asset_id', '=', asset.id),
            ('state', '=', 'assigned'),
        ], limit=1, order='assigned_date desc')
        if active:
            active.action_return()

        asset.write({'status': 'not_in_use'})

        return request.render('zakheni_asset_management.asset_scan_message', {
            'title': 'Status Updated',
            'message': f'Asset {asset.display_name} has been marked as Not in Use.',
        })
