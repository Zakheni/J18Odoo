import json
import logging
import re
import traceback
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_enrich_date = fields.Datetime('Last Enrichment Date', readonly=True)
    enrich_status = fields.Selection([
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('error', 'Error'),
    ], string='Enrichment Status', readonly=True, default=False)

    def action_enrich_from_web(self):
        self.ensure_one()
        icp = self.env['ir.config_parameter'].sudo()
        api_key = icp.get_param('zakheni_partner_enrich.google_api_key', '')
        cx = icp.get_param('zakheni_partner_enrich.google_cx', '')
        if not api_key or not cx:
            raise UserError(
                _('Google Custom Search API key and Search Engine ID (cx) must be configured in Settings > General Settings > Zakheni Partner Enrich.')
            )
        data = self._enrich_by_name(api_key, cx)
        if not data:
            raise UserError(_('No enrichment data found for "%s".') % self.name)
        self._apply_enrichment(data)
        self.write({
            'last_enrich_date': fields.Datetime.now(),
            'enrich_status': 'success',
        })
        self._enrichment_message_post(data)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def _enrich_by_name(self, api_key, cx):
        self.ensure_one()
        query = self.name
        if self.vat:
            query = f'{query} {self.vat}'
        url = 'https://www.googleapis.com/customsearch/v1'
        params = {
            'key': api_key,
            'cx': cx,
            'q': query,
            'num': 5,
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            _logger.error('Google search failed for %s: %s', query, e)
            return {}
        items = result.get('items', [])
        if not items:
            return {}
        best = items[0]
        data = {
            'website': best.get('link', ''),
            'description': best.get('snippet', ''),
        }
        pagemap = best.get('pagemap', {})
        if pagemap.get('organization'):
            org = pagemap['organization'][0]
            data['name'] = org.get('name') or data.get('name')
            data['description'] = org.get('description') or data.get('description')
            data['logo'] = org.get('logo')
        if pagemap.get('hcard'):
            hcard = pagemap['hcard'][0]
            data['phone'] = hcard.get('tel')
            data['email'] = hcard.get('email')
            data['street'] = hcard.get('adr-street-address')
            data['city'] = hcard.get('adr-locality')
            data['state'] = hcard.get('adr-region')
            data['zip'] = hcard.get('adr-postal-code')
            data['country'] = hcard.get('adr-country-name')
        scraped = self._scrape_website(best.get('link', ''))
        data.update({k: v for k, v in scraped.items() if v and not data.get(k)})
        return data

    def _scrape_website(self, url):
        if not url:
            return {}
        try:
            resp = requests.get(url, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            _logger.warning('Failed to scrape %s: %s', url, e)
            return {}
        data = {}
        body = soup.find('body')
        text = body.get_text() if body else soup.get_text()
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        valid_emails = [e for e in emails if not e.startswith('noreply')]
        if valid_emails:
            data['email'] = valid_emails[0]
        phone_pattern = re.compile(
            r'(?:\+?27|0)[\s-]?(?:\d[\s-]?){8,10}'
            r'|(?:\+?\d{1,3})?[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}'
        )
        phones = phone_pattern.findall(text)
        if phones:
            data['phone'] = phones[0].strip()
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            data['description'] = meta_desc['content']
        return data

    def _apply_enrichment(self, data):
        self.ensure_one()
        vals = {}
        if data.get('name') and not self.is_company:
            vals['name'] = data['name']
        if data.get('website') and not self.website:
            parsed = urlparse(data['website'])
            vals['website'] = parsed.netloc or parsed.path
        if data.get('email') and not self.email:
            vals['email'] = data['email']
        if data.get('phone') and not self.phone:
            vals['phone'] = data['phone']
        if data.get('street') and not self.street:
            vals['street'] = data['street']
        if data.get('city') and not self.city:
            vals['city'] = data['city']
        if data.get('zip') and not self.zip:
            vals['zip'] = data['zip']
        if data.get('country') and not self.country_id:
            country = self.env['res.country'].search([('name', '=ilike', data['country'])], limit=1)
            if country:
                vals['country_id'] = country.id
        if data.get('description') and not self.comment:
            vals['comment'] = data['description']
        if vals:
            self.write(vals)

    def _enrichment_message_post(self, data):
        self.ensure_one()
        msg = _('<b>Partner enriched from web search</b><br/>') + '<ul>'
        enriched = []
        if data.get('website'):
            enriched.append(_('Website: %s') % data['website'])
        if data.get('email'):
            enriched.append(_('Email: %s') % data['email'])
        if data.get('phone'):
            enriched.append(_('Phone: %s') % data['phone'])
        if data.get('street'):
            enriched.append(_('Address: %s, %s %s') % (
                data.get('street', ''),
                data.get('city', ''),
                data.get('zip', ''),
            ))
        if data.get('description'):
            enriched.append(_('Description: %s') % data['description'][:200])
        if data.get('logo'):
            enriched.append(_('Logo found'))
        if enriched:
            msg += '<li>' + '</li><li>'.join(enriched) + '</li>'
        msg += '</ul>'
        self.message_post(body=msg, subtype_xmlid='mail.mt_note')
