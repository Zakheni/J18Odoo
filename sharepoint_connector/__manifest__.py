{
    'name': 'SharePoint Connector',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Sync documents and lists between Odoo and SharePoint Online',
    'depends': ['base', 'mail', 'dms', 'microsoft_account'],
    'data': [
        'security/ir.model.access.csv',
        'data/sharepoint_data.xml',
        'views/sharepoint_views.xml',
    ],
    'external_dependencies': {
        'python': ['office365'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
