import json
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class TenderAiAnalysis(models.Model):
    _name = 'tender.ai.analysis'
    _description = 'AI Tender Analysis'
    _rec_name = 'tender_id'
    _order = 'create_date desc'

    tender_id = fields.Many2one('tender.tender', string='Tender', required=True, ondelete='cascade')
    document_id = fields.Many2one('tender.document', string='Source Document')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], string='Status', default='pending')
    provider = fields.Selection([
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('custom', 'Custom API'),
    ], string='AI Provider', default='openai')

    raw_response = fields.Text(string='Raw Response')
    error_message = fields.Text(string='Error Message')

    requirements = fields.Text(string='Extracted Requirements')
    deadlines = fields.Text(string='Key Deadlines')
    compliance_items = fields.Text(string='Compliance Items')
    risk_factors = fields.Text(string='Risk Factors')
    summary = fields.Text(string='Executive Summary')
    bid_recommendation = fields.Selection([
        ('recommended', 'Recommended'),
        ('not_recommended', 'Not Recommended'),
        ('needs_review', 'Needs Review'),
    ], string='Bid Recommendation')
    confidence_score = fields.Float(string='Confidence Score (%)')

    def action_analyze(self):
        self.state = 'processing'
        try:
            result = self._call_ai_api()
            self.write(result)
            self.state = 'completed'
        except Exception as e:
            _logger.error("AI analysis failed for tender %s: %s", self.tender_id.display_name, e)
            self.error_message = str(e)
            self.state = 'error'
        return True

    def _call_ai_api(self):
        ir_config = self.env['ir.config_parameter']
        api_key = ir_config.get_param('zakheni_tender.ai_api_key', '')
        if not api_key:
            raise ValueError("AI API key not configured. Set zakheni_tender.ai_api_key in Settings.")

        document_text = self._get_document_text()
        prompt = self._build_prompt(document_text)

        if self.provider == 'openai':
            return self._call_openai(api_key, prompt)
        elif self.provider == 'anthropic':
            return self._call_anthropic(api_key, prompt)
        else:
            return self._call_custom(api_key, prompt)

    def _get_document_text(self):
        if self.document_id and self.document_id.datas:
            import base64
            try:
                data = base64.b64decode(self.document_id.datas)
                return data.decode('utf-8', errors='replace')[:50000]
            except Exception:
                return "[Binary document - text extraction not available]"
        return "[No document attached]"

    def _build_prompt(self, document_text):
        return f"""Analyze this tender document and provide structured output as JSON:

Document:
{document_text}

Respond with this exact JSON structure (no markdown):
{{
    "summary": "2-3 sentence executive summary",
    "requirements": ["list of key requirements"],
    "deadlines": ["list of key deadlines found"],
    "compliance_items": ["list of compliance requirements"],
    "risk_factors": ["list of potential risks"],
    "bid_recommendation": "recommended|not_recommended|needs_review",
    "confidence_score": 0-100
}}"""

    def _call_openai(self, api_key, prompt):
        import requests
        resp = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'gpt-4o-mini',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.1,
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()['choices'][0]['message']['content']
        return self._parse_ai_response(content)

    def _call_anthropic(self, api_key, prompt):
        import requests
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 2000,
                'messages': [{'role': 'user', 'content': prompt}],
            },
            timeout=120,
        )
        resp.raise_for_status()
        content = resp.json()['content'][0]['text']
        return self._parse_ai_response(content)

    def _call_custom(self, api_key, prompt):
        ir_config = self.env['ir.config_parameter']
        endpoint = ir_config.get_param('zakheni_tender.ai_custom_endpoint', '')
        if not endpoint:
            raise ValueError("Custom API endpoint not configured.")
        import requests
        resp = requests.post(
            endpoint,
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'prompt': prompt},
            timeout=120,
        )
        resp.raise_for_status()
        return self._parse_ai_response(resp.text)

    def _parse_ai_response(self, content):
        content = content.strip()
        if content.startswith('```'):
            content = content.split('\n', 1)[1]
            content = content.rsplit('```', 1)[0]
        data = json.loads(content.strip())

        return {
            'raw_response': json.dumps(data),
            'summary': data.get('summary', ''),
            'requirements': '\n'.join(data.get('requirements', [])),
            'deadlines': '\n'.join(data.get('deadlines', [])),
            'compliance_items': '\n'.join(data.get('compliance_items', [])),
            'risk_factors': '\n'.join(data.get('risk_factors', [])),
            'bid_recommendation': data.get('bid_recommendation', 'needs_review'),
            'confidence_score': data.get('confidence_score', 0),
        }
