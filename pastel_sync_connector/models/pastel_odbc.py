import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import pyodbc
except ImportError:
    pyodbc = None


class PastelOdbcManager(models.AbstractModel):
    _name = 'pastel.odbc.manager'
    _description = 'Pastel ODBC Connection Manager'

    @api.model
    def get_connection(self):
        if pyodbc is None:
            raise UserError(_(
                'The pyodbc library is required but not installed. '
                'Run: pip install pyodbc'
            ))

        ICP = self.env['ir.config_parameter'].sudo()
        dsn = ICP.get_param('pastel_sync.odbc_dsn', 'PastelPartner')
        user = ICP.get_param('pastel_sync.odbc_user', '')
        password = ICP.get_param('pastel_sync.odbc_password', '')

        conn_str = f'DSN={dsn}'
        if user:
            conn_str += f';UID={user}'
        if password:
            conn_str += f';PWD={password}'

        try:
            conn = pyodbc.connect(conn_str, timeout=30)
            _logger.info('Connected to Pastel Partner via ODBC (DSN: %s)', dsn)
            return conn
        except Exception as e:
            raise UserError(_(
                'Failed to connect to Pastel Partner ODBC (DSN: %(dsn)s):\n%(error)s',
                dsn=dsn, error=str(e)
            ))

    @api.model
    def execute_query(self, sql, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(sql, params)
                else:
                    cursor.execute(sql)
                if sql.strip().upper().startswith(('SELECT', 'WITH')):
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            _logger.error('Pastel query failed: %s\nSQL: %s', e, sql)
            raise UserError(_('Pastel query error: %s') % str(e))
        finally:
            conn.close()

    @api.model
    def get_tables(self):
        return self.execute_query(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE='TABLE' ORDER BY TABLE_NAME"
        )

    @api.model
    def get_columns(self, table_name):
        return self.execute_query(
            "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH "
            "FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ? "
            "ORDER BY ORDINAL_POSITION",
            [table_name]
        )

    @api.model
    def validate_connection(self):
        try:
            tables = self.get_tables()
            return {
                'connected': True,
                'table_count': len(tables),
                'tables': [t['TABLE_NAME'] for t in tables[:20]],
            }
        except Exception as e:
            return {'connected': False, 'error': str(e)}
