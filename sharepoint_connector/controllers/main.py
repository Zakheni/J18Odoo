import base64
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class SharePointController(http.Controller):

    @http.route('/sharepoint/browse', type='json', auth='user')
    def browse_site(self, site_id):
        site = request.env['sharepoint.site'].browse(site_id)
        if not site.exists():
            return {'error': 'Site not found'}
        try:
            client = site._get_client()
            web = client.web
            client.load(web)
            lists_data = client.web.lists
            client.load(lists_data)
            client.execute_query()
            libraries = [{'id': l.id, 'title': l.title, 'item_count': l.item_count} for l in lists_data]
            return {'site_title': web.title, 'libraries': libraries}
        except Exception as e:
            _logger.exception('SharePoint browse failed')
            return {'error': str(e)}

    @http.route('/sharepoint/browse_library', type='json', auth='user')
    def browse_library(self, site_id, library_name):
        site = request.env['sharepoint.site'].browse(site_id)
        if not site.exists():
            return {'error': 'Site not found'}
        try:
            client = site._get_client()
            sp_library = client.web.lists.get_by_title(library_name)
            client.load(sp_library)
            items = sp_library.items
            client.load(items)
            client.execute_query()
            files = [{'id': i.id, 'title': i.properties.get('Title', '')} for i in items]
            return {'files': files, 'library': library_name}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/sharepoint/upload', type='json', auth='user')
    def upload_file(self, site_id, library_name, file_name, file_data):
        site = request.env['sharepoint.site'].browse(site_id)
        if not site.exists():
            return {'error': 'Site not found'}
        try:
            client = site._get_client()
            target_folder = client.web.lists.get_by_title(library_name).root_folder
            client.load(target_folder)
            client.execute_query()
            file_bytes = base64.b64decode(file_data)
            target_folder.upload_file(file_name, file_bytes)
            client.execute_query()
            return {'success': True, 'file_name': file_name}
        except Exception as e:
            return {'error': str(e)}

    @http.route('/sharepoint/download', type='json', auth='user')
    def download_file(self, site_id, file_url):
        site = request.env['sharepoint.site'].browse(site_id)
        if not site.exists():
            return {'error': 'Site not found'}
        try:
            client = site._get_client()
            from office365.sharepoint.files.file import File
            file = File.open_binary(client, file_url)
            file_content = base64.b64encode(file.content).decode('utf-8')
            return {'success': True, 'file_name': file_url.split('/')[-1], 'file_data': file_content}
        except Exception as e:
            return {'error': str(e)}
