{
    'name': 'Zakheni Asset Management',
    'version': '18.0.1.2.0',
    'author': 'Zakheni ICT (Pty) Ltd',
    'license': 'LGPL-3',
    'category': 'Accounting/Assets',
    'summary': 'Full asset lifecycle management with depreciation, assignments, maintenance, and barcodes',
    'description': """
Combined physical and accounting asset management:
- Asset categories with hierarchical structure and default depreciation rules
- Employee check-in/check-out with assignment history
- Location tracking (room, site, warehouse)
- Preventive and corrective maintenance with work logs
- Barcode and QR code generation
- Lifecycle status workflow: draft -> in_use -> maintenance -> disposed
- Straight-line and reducing-balance depreciation schedules
- Reporting dashboard with KPIs and breakdowns
""",
    'depends': [
        'base',
        'mail',
        'hr',
        'account',
        'barcodes',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/asset_security_groups.xml',
        'data/asset_sequence.xml',
        'data/asset_data.xml',
        'data/asset_qr_init.xml',
        'views/asset_category_views.xml',
        'views/asset_location_views.xml',
        'views/asset_asset_views.xml',
        'views/asset_assignment_views.xml',
        'views/asset_maintenance_views.xml',
        'views/asset_depreciation_views.xml',
        'views/asset_dashboard_views.xml',
        'views/asset_audit_views.xml',
        'views/asset_bulk_update_views.xml',
        'views/res_config_settings_views.xml',
        'views/menus.xml',
        'views/asset_scan_templates.xml',
        'report/asset_report_views.xml',
        'report/qr_label.xml',
    ],
    'demo': [
        'data/asset_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zakheni_asset_management/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
