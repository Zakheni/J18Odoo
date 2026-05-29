import base64
import json

from markupsafe import escape
from psycopg2 import IntegrityError
from werkzeug.exceptions import BadRequest

from odoo import http, SUPERUSER_ID, _
from odoo.http import request
from odoo.addons.website.controllers.form import WebsiteForm
from odoo.exceptions import AccessDenied, ValidationError, UserError
import rsaidnumber

class WebsiteFormInherit(WebsiteForm):

    def extract_data(self, model, values):
        dest_model = request.env[model.sudo().model]
        data = {
            'record': {},  # Values to create record
            'attachments': [],  # Attached files
            'custom': '',  # Custom fields values
            'meta': '',  # Add metadata if enabled
        }

        authorized_fields = model.with_user(SUPERUSER_ID)._get_form_writable_fields()
        error_fields = []
        custom_fields = []

        for field_name, field_value in values.items():
            if hasattr(field_value, 'filename'):
                field_name = field_name.split('[', 1)[0]
                if model.name == 'Applicant' and field_name == 'Resume':
                    attachment_value = {
                        'name': field_value.filename,
                        'datas': base64.encodebytes(field_value.read()),
                        'res_model': 'hr.applicant',
                    }
                    attachment_id = request.env['ir.attachment'].sudo().create(attachment_value)
                    data['record']['resume_copy'] = attachment_id.id
                    field_value.stream.seek(0)
                elif field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                    field_value.stream.seek(0)  # do not consume value forever
                    if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                        data['record'][field_name + "_filename"] = field_value.filename
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

                if dest_model._name == 'mail.mail' and field_name == 'email_from':
                    custom_fields.append((_('email'), field_value))

            # If it's a custom field
            elif field_name not in ('context', 'website_form_signature'):
                custom_fields.append((field_name, field_value))

        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        # Add metadata if enabled  # ICP for retrocompatibility
        if request.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ = request.httprequest.headers.environ
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP", environ.get("REMOTE_ADDR"),
                "USER_AGENT", environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER", environ.get("HTTP_REFERER")
            )
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items() if
                                   field['required'] and label not in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)
        if model.name == 'Applicant':
            data['custom'] = ''
            fields_list = request.env['hr.applicant']._fields.keys()
            for val in values:
                if val in fields_list:
                    if val == 'citizenship' and values['citizenship'] == 'SA':
                        id_number = rsaidnumber.parse(values['id_no'])
                        data.get('record').update({'nationality_id': request.env.ref('base.za').id,
                                                   'date_of_birth': id_number.date_of_birth})
                    elif val == 'is_create_resume_from_web' and values[val] == 'on':
                        data.get('record').update({val: True})
                    elif val == 'is_create_resume_from_web' and values[val] == 'on':
                        data.get('record').update({val: False})
                    else:
                        data.get('record').update({val: values[val]})
                if val == 'is_create_resume':
                    data['custom'] = 'create_resume'
        return data


    @http.route('/validate/nationalityId', type='json', auth='public')
    def Validate_nationality_id(self, id_number):
            try:
                id_number = rsaidnumber.parse(id_number)
                if id_number.valid:
                    return True
            except:
                return False

    @http.route('/website/resume/create', type='http', auth="public", methods=['POST'], csrf=False, website=True)
    def job_applicant_resume_create(self, **kwargs):
        if kwargs.get('applicant_id'):
            applicant_id = request.env['hr.applicant'].sudo().browse(int(kwargs.get('applicant_id')))

            # Qualification ids
            qual_dict = {}
            for key, value in kwargs.items():
                if key.startswith(('qualification', 'institute', 'year')):
                    index = key[-1]
                    qual_dict.setdefault(index, {}).update({key[:-1]: value})
            qual_list = [(0, 0, {**value}) for value in qual_dict.values()]

            # Course ids
            course_dict = {}
            for key, value in kwargs.items():
                if key.startswith(('course', 'course_institute')):
                    index = key[-1]
                    course_dict.setdefault(index, {}).update({key[:-1]: value})
            course_list = [(0, 0, {**value}) for value in course_dict.values()]

            # employment History ids
            employment_history_dict = {}
            for key, value in kwargs.items():
                if key.startswith(('emp_company_name', 'emp_date_employed', 'emp_position', 'emp_duties')):
                    index = key[-1]
                    employment_history_dict.setdefault(index, {}).update({key[:-1]: value})
            employment_history_list = [(0, 0, {**value}) for value in employment_history_dict.values()]
            # Skill ids
            skill_dict = {}
            for key, value in kwargs.items():
                if key != 'skills_summary':
                    if key.startswith(('skill', 'skill_experience', 'skill_level')):
                        index = key[-1]
                        skill_dict.setdefault(index, {}).update({key[:-1]: value})
            skill_list = [(0, 0, {**value}) for value in skill_dict.values()]

            # Reference ids
            reference_dict = {}
            for key, value in kwargs.items():
                if key.startswith(('ref_company', 'ref_person', 'ref_person_contact_details')):
                    index = key[-1]
                    reference_dict.setdefault(index, {}).update({key[:-1]: value})
            reference_list = [(0, 0, {**value}) for value in reference_dict.values()]
            values = {k: v for k, v in kwargs.items() if not k[-1].isdigit()}
            values.update({
                'applicant_id': applicant_id.id,
                'qualification_ids': qual_list,
                'course_ids': course_list,
                'employment_history_ids': employment_history_list,
                'skill_ids': skill_list,
                'reference_ids': reference_list,
            })
            existing_applicant = request.env['hr.applicant.resume'].sudo().search([('applicant_id', '=', applicant_id.id)], limit=1)
            if existing_applicant:
                existing_applicant.write({
                    'qualification_ids': [(5, 0, 0)],
                    'course_ids': [(5, 0, 0)],
                    'employment_history_ids': [(5, 0, 0)],
                    'skill_ids': [(5, 0, 0)],
                })
                existing_applicant.sudo().write(values)
            else:
                request.env['hr.applicant.resume'].sudo().create(values)
            applicant_id.is_create_resume_from_web = False
        return request.render("website_hr_recruitment.thankyou")