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
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/stages.xml',
        'views/tender_stage_views.xml',
        'views/tender_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
