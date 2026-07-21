import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PastelSyncController(http.Controller):

    @http.route('/pastel_sync/status', type='json', auth='user')
    def get_status(self):
        log_model = request.env['pastel.sync.log']
        last_log = log_model.search([], limit=1)
        if last_log:
            return {
                'last_sync': last_log.create_date.isoformat() if last_log.create_date else None,
                'state': last_log.state,
                'scope': last_log.scope,
                'return_code': last_log.return_code,
            }
        return {'last_sync': None, 'state': None}

    @http.route('/pastel_sync/test_connection', type='json', auth='user')
    def test_connection(self):
        result = request.env['pastel.odbc.manager'].validate_connection()
        return result

    @http.route('/pastel_sync/config', type='json', auth='user')
    def get_config(self):
        ICP = request.env['ir.config_parameter'].sudo()
        return {
            'odbc_dsn': ICP.get_param('pastel_sync.odbc_dsn', ''),
            'odbc_user': ICP.get_param('pastel_sync.odbc_user', ''),
            'odbc_password': bool(ICP.get_param('pastel_sync.odbc_password', '')),
        }
