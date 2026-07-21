import base64
import io
import logging

import qrcode
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AssetQR(models.Model):
    _inherit = 'asset.asset'

    qr_code = fields.Binary(string='QR Code', attachment=True, copy=False)
    qr_code_uri = fields.Char(string='QR Code URI', compute='_compute_qr_code_uri')

    @api.depends('qr_code')
    def _compute_qr_code_uri(self):
        for rec in self:
            if rec.qr_code:
                try:
                    data = rec.qr_code
                    rec.qr_code_uri = 'data:image/png;base64,%s' % (data.decode() if isinstance(data, bytes) else data)
                except Exception:
                    rec.qr_code_uri = False
            else:
                rec.qr_code_uri = False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if not rec.barcode:
                rec._generate_barcode()
            rec._generate_qr_code()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'barcode' in vals or 'name' in vals:
            for rec in self:
                rec._generate_qr_code()
        return res

    def _generate_barcode(self):
        for rec in self:
            if not rec.barcode:
                seq = self.env['ir.sequence'].next_by_code('zakheni.asset.asset') or 'AST-00001'
                rec.barcode = seq

    def _get_scan_url(self):
        base = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://localhost:8069')
        base = base.rstrip('/')
        if base.startswith('http://'):
            base = 'https://' + base[7:]
        barcode = self.barcode or self.code or ''
        return f'{base}/asset/scan/{barcode}'

    def _generate_qr_code(self):
        for rec in self:
            try:
                data = rec._get_scan_url()
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=6,
                    border=2,
                )
                qr.add_data(data)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black', back_color='white')
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)
                rec.qr_code = base64.b64encode(buf.read()).decode()
            except Exception as e:
                _logger.warning('Failed to generate QR for asset %s: %s', rec.code, e)

    def action_generate_qr_now(self):
        self._generate_qr_code()
        return {'type': 'ir.actions.act_window_close'}

    def action_bulk_update_status(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Status',
            'res_model': 'asset.bulk.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_asset_ids': self.ids},
        }

    def action_print_qr_label(self):
        return self.env.ref('zakheni_asset_management.action_report_qr_label').report_action(self)

    @api.model
    def _init_qr_codes(self):
        assets = self.search([('barcode', '!=', False)])
        if assets:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', 'asset.asset'),
                ('res_field', '=', 'qr_code'),
            ])
            if attachments:
                attachments.unlink()
            assets._generate_qr_code()
        return True
