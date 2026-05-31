{
    'name': 'Zakheni ICT Helpdesk — Customer Team Routing',
    'summary': 'Assign customers to helpdesk teams with automatic ticket routing.',
    'version': '18.0.1.0.0',
    'category': 'Services/Helpdesk',
    'license': 'LGPL-3',
    'author': 'Zakheni ICT (Pty) Ltd',
    'website': 'https://www.zakhenict.co.za',
    'depends': [
        'helpdesk_mgmt',
        'helpdesk_mgmt_customer',
    ],
    'data': [
        'views/res_partner_views.xml',
        'views/helpdesk_ticket_team_views.xml',
        'views/helpdesk_ticket_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
