{
    'name': 'Timesheet Dashboard',
    'version': '18.0.1.0.0',
    'category': 'Timesheets/Analytics',
    'summary': '''
        This is the Timesheet Analytics dahsboard that gives an overall overview of the employee's time spent on project/task basis analysis.
    ''',
    'description': '''
        The user with interests to the project management analytics can see how each employee from any department are spending time on the assigned projects and tasks.
    ''',
    'author': 'Zakheni ICT',
    'depends': ['hr_timesheet'],
    'data': [
        'security/ir.model.access.csv',
        'data/organization_data.xml',
        'views/hr_organization_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_timesheet_line_views.xml',
        'views/views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'timesheet_analytics/static/src/css/timesheet_dashboard.css',
            'timesheet_analytics/static/src/js/timesheet_dashboard.js',
            'timesheet_analytics/static/src/xml/timesheet_dashboard.xml'
            
        ],
    },
    'images': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    
}
