{
    'name': 'Web Timesheet',
    'website': 'https://www.zakhenict.co.za',
    'live_test_url': 'https://demo.zakhenict.co.za',
    'summary': """ Web Timesheet""",
    'description': """Web Timesheet""",

    'author': 'Zakheni ICT (Pty) Ltd',
    'version': '18.0.1.0.0',
    'category': 'Website',
    'depends': ['portal', 'project', 'hr', 'hr_timesheet'],
    'data': [
        'views/templates.xml',
        'views/portal.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'web_timesheet/static/src/js/custom.js',
            'web_timesheet/static/src/js/portal_timesheet.js',
            'web_timesheet/static/src/scss/custom.scss',
        ],
    },
   
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False
}
