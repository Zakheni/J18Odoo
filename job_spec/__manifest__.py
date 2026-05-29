{
    'name': 'Zakheni ICT Recruitment (Enterprise)',
    'website': 'https://www.zakhenict.co.za',
    'category': 'Recruitment',
    'summary': 'Recruitment customisation.',
    'description': """
Recruitment customisation
""",
    'author': 'Zakheni ICT Pty(Ltd)',
    'version': '18.0.0.1.0',
    'depends': ['hr_recruitment', 'website', 'website_hr_recruitment', 'l10n_za'],
    "data": [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/job_spec.xml',
        'views/hr_applicant_view.xml',
        'views/hr_applicant_resume.xml',
        'views/website_recruitment_templates.xml',
        'wizards/import_resume.xml',
        'wizards/import_zakheni_resume.xml',
        'report/resume_report.xml'
    ],
    'external_dependencies': {
        'python': ['rsaidnumber', 'camelot', 'python-docx'],
        # can be install using command "pip install rsa-id-number".
    },
    'assets': {
            'web.assets_frontend': [
                'job_spec/static/src/js/job_application_portal.js',
                'job_spec/static/src/scss/**/*',
            ],
    },
    'license': 'LGPL-3',
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
