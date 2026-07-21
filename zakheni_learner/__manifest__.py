{
    "name": "Zakheni Learner Management",
    "version": "18.0.1.0.0",
    "author": "Zakheni ICT (Pty) Ltd",
    "category": "Human Resources",
    "license": "AGPL-3",
    "website": "https://zakheni.co.za",
    "depends": ["base", "mail"],
    "data": [
        "security/zakheni_learner_security.xml",
        "security/ir.model.access.csv",
        "views/res_users.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
