# ruff: noqa: B018
{
    'name': 'Zakheni Hybrid Attendance',
    'summary': 'Hybrid workforce attendance: work locations, planned vs actual, '
               'exceptions, approvals, register, dashboard.',
    'version': '18.0.1.0.0',
    'category': 'Human Resources/Attendances',
    'license': 'LGPL-3',
    'author': 'Zakheni ICT (Pty) Ltd',
    'website': 'https://www.zakhenict.co.za',
    'depends': [
        'hr_attendance',
        'hr_holidays',
    ],
    'data': [
        'security/zakheni_attendance_groups.xml',
        'security/ir.model.access.csv',
        'security/zakheni_attendance_rules.xml',
        'data/zakheni_work_location_data.xml',
        'data/zakheni_attendance_cron.xml',
        'views/zakheni_work_location_views.xml',
        'views/hr_employee_views.xml',
        'views/resource_calendar_attendance_views.xml',
        'views/hr_attendance_views.xml',
        'views/zakheni_attendance_day_views.xml',
        'views/res_config_settings_views.xml',
        'views/zakheni_attendance_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zakheni_hybrid_attendance/static/src/js/dashboard.js',
            'zakheni_hybrid_attendance/static/src/scss/zakheni_attendance.scss',
            'zakheni_hybrid_attendance/static/src/xml/zakheni_attendance_templates.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
