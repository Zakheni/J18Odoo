{
    'name': 'Web Timesheet Analytics',
    'version': '18.0.1.0.0',
    'summary': 'Portal dashboard for employee-linked timesheet analytics',
    'description': 'Provides a portal analytics dashboard linked to the logged-in user employee.',
    'author': 'Zakheni ICT',
    'category': 'Website',
    'depends': ['web_timesheet', 'timesheet_analytics'],
    'data': [
        'views/portal_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'timesheet_analytics/static/src/css/timesheet_dashboard.css',
            'timesheet_analytics/static/src/xml/timesheet_dashboard.xml',
            'timesheet_analytics/static/src/js/timesheet_dashboard.js',
            'web_timesheet_analytics/static/src/js/portal_timesheet_dashboard.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
