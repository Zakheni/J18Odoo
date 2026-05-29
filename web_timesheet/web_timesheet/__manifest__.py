
{
    'name': 'Web Timesheet',
    'website': 'https://www.zakhenict.co.za',
    'demo': 'https://demo.zakhenict.co.za',
    'summary': """ Web Timesheet""",
    'description': """Web Timesheet""",

    'author': 'Zakheni ICT (Pty) Ltd',
    'version': '16.0.1.0.0',
    'category': 'Website',
    'depends': ['website', 'project', 'hr', 'timesheet_grid'],
    'versions': {
        'supported_odoo_versions': ['16.0'],
        'minimum_version': '16.0',
        'maximum_version': '16.0'
    },
    'data': [
        'views/templates.xml',
        'views/portal.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'web_timesheet/static/src/js/custom.js',
        ],
    },
   
    'license': 'LGPL-3',
    'demo': 'https://demo.zakhenict.co.za',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'price': 60,
    'currency': "USD"
}
