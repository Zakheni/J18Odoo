from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pastel_sync_odbc_dsn = fields.Char(
        string='Pastel ODBC DSN',
        default_model='ir.config_parameter',
        config_parameter='pastel_sync.odbc_dsn',
    )
    pastel_sync_odbc_user = fields.Char(
        string='Pastel ODBC User',
        default_model='ir.config_parameter',
        config_parameter='pastel_sync.odbc_user',
    )
    pastel_sync_odbc_password = fields.Char(
        string='Pastel ODBC Password',
        default_model='ir.config_parameter',
        config_parameter='pastel_sync.odbc_password',
    )

    def action_test_pastel_connection(self):
        result = self.env['pastel.odbc.manager'].validate_connection()
        if result.get('connected'):
            raise UserError(_(
                'Connection successful!\n\n'
                'Tables found: %(count)d\n'
                'Tables: %(tables)s',
                count=result['table_count'],
                tables=', '.join(result['tables']),
            ))
        raise UserError(_(
            'Connection failed:\n%(error)s',
            error=result.get('error', 'Unknown error'),
        ))
