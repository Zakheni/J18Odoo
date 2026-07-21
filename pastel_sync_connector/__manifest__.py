{
    'name': 'Pastel Accounting Connector',
    'version': '1.0.0',
    'category': 'Accounting',
    'summary': 'Sync partners, products, and invoices with Sage Pastel Partner',
    'description': """
        Pastel Accounting Connector
        ===========================
        Fully standalone Odoo 18 module for bidirectional sync with Sage Pastel
        Partner accounting via ODBC. No external services required.
    """,
    'author': 'Odoo Pastel Connector',
    'website': 'https://github.com/odoo-pastel-connector',
    'depends': ['base', 'product', 'account'],
    'external_dependencies': {
        'python': ['pyodbc'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/pastel_settings_view.xml',
        'views/res_partner_view.xml',
        'views/product_product_view.xml',
        'views/account_move_view.xml',
        'views/pastel_sync_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
