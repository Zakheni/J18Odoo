{
    "name": "Helpdesk Customer Isolation",
    "summary": """
        Per-customer helpdesk with dedicated email aliases,
        auto-routing, and filtered portal access.
    """,
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "category": "After-Sales",
    "author": "Zakheni ICT",
    "depends": [
        "helpdesk_mgmt",
        "mail",
        "portal",
        "im_livechat",
        "website_livechat",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/helpdesk_customer_security.xml",
        "data/helpdesk_customer_data.xml",
        "views/res_partner_views.xml",
        "views/helpdesk_ticket_customer_views.xml",
        "views/helpdesk_ticket_team_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/helpdesk_portal_templates.xml",
    ],
    "demo": [],
    "assets": {},
    "development_status": "Alpha",
    "application": False,
    "installable": True,
    "auto_install": False,
}
