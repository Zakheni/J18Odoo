{
    "name": "CV Studio",
    "version": "18.0.1.0.0",
    "summary": "Standardise candidate CV packs into the Zakheni house format, with AI drafting",
    "description": """
CV Studio
=========

Ingest a pack of candidate CVs (a zip or a server folder), auto-draft each
candidate into the Zakheni house format, review and edit the result in Odoo, then
generate the standardised DOCX + PDF and collect the supporting documents - all
from inside Odoo.

The drafting engine is the same one used by the desktop CV standardiser: a fast
heuristic parser, or AI curation that shells out to a local ``opencode`` install
(no API keys). Each candidate is a record you can edit before generating.
""",
    "author": "Jermaine / Zakheni ICT",
    "website": "https://zakheni.co.za",
    "category": "Human Resources/Recruitment",
    "license": "LGPL-3",
    "depends": ["base"],
    "external_dependencies": {"python": []},
    "data": [
        "security/cv_studio_security.xml",
        "security/ir.model.access.csv",
        "data/cv_studio_data.xml",
        "views/cv_candidate_views.xml",
        "views/cv_pack_views.xml",
        "views/cv_studio_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "cv_studio/static/src/dropzone/cv_dropzone.js",
            "cv_studio/static/src/dropzone/cv_dropzone.xml",
            "cv_studio/static/src/dropzone/cv_dropzone.css",
        ],
    },
}
