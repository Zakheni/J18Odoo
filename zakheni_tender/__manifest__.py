{
    'name': 'Zakheni Tender Management',
    'summary': 'Track and manage tenders you are bidding on',
    'version': '18.0.1.0.0',
    'category': 'Services/Project',
    'license': 'LGPL-3',
    'author': 'Zakheni ICT (Pty) Ltd',
    'website': 'https://www.zakhenict.co.za',
    'depends': [
        'mail',
        'portal',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/stages.xml',
        'views/tender_stage_views.xml',
        'views/tender_views.xml',
        'views/dashboard_views.xml',
        'views/analysis_views.xml',
        'views/portal_templates.xml',
        'views/menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zakheni_tender/static/src/scss/tender_dashboard.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
