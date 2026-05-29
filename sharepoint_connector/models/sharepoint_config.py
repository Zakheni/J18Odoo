import logging

from odoo import fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from office365.runtime.auth.authentication_context import AuthenticationContext
    from office365.sharepoint.client_context import ClientContext
except ImportError:
    _logger.warning("Office365-REST-Python-Client not installed")


class SharePointConfig(models.Model):
    _name = 'sharepoint.config'
    _description = 'SharePoint Connection Configuration'
    _rec_name = 'name'

    name = fields.Char(default='SharePoint Configuration', required=True)
    tenant_id = fields.Char(string='Azure AD Tenant ID', required=True)
    client_id = fields.Char(string='Application (Client) ID', required=True)
    client_secret = fields.Char(string='Client Secret')
    use_certificate = fields.Boolean(string='Use Certificate (App-Only)')
    certificate_path = fields.Char(string='Certificate Path (.pfx)')
    certificate_password = fields.Char(string='Certificate Password')
    default_site_url = fields.Char(string='Default SharePoint Site URL')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_company', 'unique(company_id)', 'Only one configuration per company allowed!'),
    ]

    def _get_client(self, site_url=None):
        self.ensure_one()
        url = site_url or self.default_site_url
        if not url:
            raise ValidationError(_('SharePoint Site URL is required'))
        ctx = AuthenticationContext(url=url)
        if self.client_id and self.client_secret:
            ctx.acquire_token_for_app(client_id=self.client_id, client_secret=self.client_secret)
        elif self.use_certificate:
            with open(self.certificate_path, 'rb') as f:
                pfx_data = f.read()
            from office365.runtime.auth.client_certificate import ClientCertificate
            cert = ClientCertificate.from_pfx(pfx_data, self.certificate_password or '')
            ctx.acquire_token_for_app(client_id=self.client_id, certificate=cert)
        else:
            raise ValidationError(_('Either client_secret or certificate must be configured'))
        return ClientContext(url, ctx)

    def action_test_connection(self):
        self.ensure_one()
        try:
            client = self._get_client()
            web = client.web
            client.load(web)
            client.execute_query()
            return {
                'type': 'ir.actions.act_window_message',
                'title': _('Success'),
                'message': _('Connected to SharePoint: %s') % web.title,
            }
        except Exception as e:
            raise ValidationError(_('Connection failed: %s') % str(e))
