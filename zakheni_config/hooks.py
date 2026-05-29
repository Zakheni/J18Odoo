from odoo import api, SUPERUSER_ID


def post_init_hook(cr_or_env, registry=None):
    env = cr_or_env if hasattr(cr_or_env, "cr") else api.Environment(cr_or_env, SUPERUSER_ID, {})
    env['res.company']._setup_company_defaults()
