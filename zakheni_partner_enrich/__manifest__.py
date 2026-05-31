{
    'name': 'Zakheni Partner Enrich from Web',
    'summary': 'Enrich partner/company data using Google Custom Search',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'license': 'LGPL-3',
    'author': 'Zakheni ICT (Pty) Ltd',
    'website': 'https://www.zakhenict.co.za',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'wizards/enrich_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
