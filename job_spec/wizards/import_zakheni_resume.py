from pypdf import PdfReader
import base64
import io

from odoo import models, fields, api, _
import re
import tempfile
import camelot
import os
from docx import Document
from odoo.exceptions import ValidationError


class ImportResume(models.TransientModel):
    _name = 'import.zakheni.resume'
    _description = 'Zakheni Format Resume Import'

    resume = fields.Binary("Upload Resume")
    file_type = fields.Selection([('doc', 'Docx'), ('pdf', 'PDF')],
                                 default="doc", string="File Type")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    def import_zakheni_resume(self):
        """Method wrriten to extract resume data from PDF type files"""
        for record in self.attachment_ids:
            file_data = base64.b64decode(record.datas)
            self.extract_text_from_file(file_data)

    def import_dox_resume(self):
        """Method wrriten to extract resume data from Docx type files"""
        for record in self.attachment_ids:
            file_mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            print(">>>>>>>>>>>>>>>>>>>>record.datas_fname",record.name, record.name.lower().endswith('.docx'))
            if not record.mimetype == file_mimetype or not record.name.lower().endswith('.docx'):
                raise ValidationError("Invalid Document: '%s'. Please upload Docx type Document !" %(record.name))
            file_data = base64.b64decode(record.datas)
            self.extract_docx_file(file_data)


    def extract_docx_file(self, file_data):
        resume_vals = {}
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.docx') as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name
            doc = Document(temp_file_path)
            tables_data = []

            for table in doc.tables:
                table_data = []
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    table_data.append(row_data)

                # Check the first row to determine the type of table
                if not table_data or not table_data[0]:
                    continue  # Skip empty or malformed tables

                # Process personal information
                if any('Surname' in row for row in table_data):
                    resume_vals.update(self.prepare_personal_info(table_data))

                # Process qualifications
                if table_data[0] == ['Qualification', 'Institution', 'Year']:
                    rows = table_data[1:]
                    qualifications = self.prepare_qualification_vals(rows)
                    resume_vals['qualification_ids'] = qualifications

                # Process employment data with header ['Company', 'Position', 'Duration']
                elif table_data[0] == ['Company', 'Position', 'Duration']:
                    rows = table_data[1:]
                    employment_vals = self.prepare_employment_vals(rows)
                    if 'employment_history_ids' not in resume_vals:
                        resume_vals['employment_history_ids'] = []
                    resume_vals['employment_history_ids'].extend(
                        employment_vals)

                # Process detailed employment data with 'Company Name', 'Dates Employed', etc.
                elif table_data[0][0] == 'Company Name':
                    employment_vals = self.prepare_employment_vals_from_detailed_rows(
                        table_data)
                    if 'employment_history_ids' not in resume_vals:
                        resume_vals['employment_history_ids'] = []
                    resume_vals['employment_history_ids'].extend(
                        employment_vals)

                # Process skills
                elif table_data[0] == ['Skills']:
                    skills = table_data[1][0].split('\n')
                    skill_vals = [(0, 0, {'skill': skill.strip()}) for skill in
                                  skills if skill.strip()]
                    resume_vals['skill_ids'] = skill_vals

            self.env['hr.applicant.resume'].create(resume_vals)

    def prepare_personal_info(self, table):
        resume_vals = {}
        for item in table:
            if item[0].strip() == 'Surname':
                resume_vals['surname'] = item[1].strip()
            if item[0].strip() == 'First Name':
                resume_vals['first_name'] = item[1].strip()
            if item[0].strip() == 'ID Number':
                resume_vals['id_passport'] = item[1].strip()
            if item[0].strip() == 'Languages':
                resume_vals['languages'] = item[1].strip()
        return resume_vals
    def prepare_qualification_vals(self, rows):
        qualifications = []
        for row in rows:
            qualification, institution, year = row

            # Create a dictionary of field values for Odoo
            qualifications.append((0, 0, {
                'qualification': qualification,
                'institute': institution,
                'year': year
            }))
        return qualifications

    def prepare_employment_vals(self, rows):
        employment_history_vals = []
        for row in rows:
            company, position, duration = row

            # Create a dictionary of field values for Odoo
            employment_history_vals.append((0, 0, {
                'emp_company_name': company,
                'emp_position': position,
                'emp_date_employed': duration
            }))
        return employment_history_vals

    def prepare_employment_vals_from_detailed_rows(self, table_data):

        employment_vals = []
        current_record = {}
        duties_list = []
        projects_list = []

        for row in table_data:
            if row[0] == 'Company Name':
                if current_record:
                    employment_vals.append((0, 0, current_record))
                    current_record = {}
                    projects_list = []
                    duties_list = []

                current_record['emp_company_name'] = row[1]

            elif row[0] == 'Dates Employed':
                current_record['emp_date_employed'] = row[1]

            elif row[0] == 'Position':
                current_record['emp_position'] = row[1]

            elif row[0].startswith('Projects:') or row[0].startswith('Duties:'):
                projects_list.append(row[0])
        if current_record:
            combined_duties = '\n'.join(projects_list)
            current_record['emp_duties'] = self.format_duties_as_html(
                combined_duties)
            employment_vals.append((0, 0, current_record))
        # fd
        return employment_vals

    def format_duties_as_html(self, duties_text):
        lines = duties_text.split('\n')
        html_content = []
        is_bullet_list_open = False

        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                continue

            if 'Projects' in stripped_line or 'Duties' in stripped_line:
                if is_bullet_list_open:
                    html_content.append('</ul>')
                    is_bullet_list_open = False
                html_content.append(
                    f'<p><b>{stripped_line}</b></p>')
            else:
                if not is_bullet_list_open:
                    html_content.append('<ul>')
                    is_bullet_list_open = True
                html_content.append(f'<li>{stripped_line}</li>')

        if is_bullet_list_open:
            html_content.append('</ul>')
        return ''.join(html_content)

    def extract_text_from_file(self, file_data):

        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix='.pdf') as temp_file:
            temp_file.write(file_data)
            temp_file_path = temp_file.name
        # Extract tables with camelot
        tables = camelot.read_pdf(temp_file_path, pages="all", flavor="lattice",
                                  line_scale=70, line_tol=3, split_text=True,
                                  shift_text=["h"])

        tables = camelot.read_pdf(temp_file_path, pages="all", flavor='stream', edge_tol=1000)
        # camelot.plot(tables[0], kind='contour')

        extracted_data = []
        for table in tables:
            print(">....................", table.df)
            extracted_data.extend(table.df.to_dict(orient="records"))
        self.create_resume_from_pdf(extracted_data)

        # Cleanup temporary file
        os.remove(temp_file_path)

    def create_resume_from_pdf(self, extracted_data):
        # Extract primary details
        resume_vals = {}
        for item in extracted_data:
            if 'Surname' in item.get(0, ''):
                print(">>>>>>>>>>>>>>>>>>>>>>.", item.get(1), item.get(2, ''), item)
                resume_vals["surname"] = item.get(1, '') + item.get(2, '')
            elif 'First Name' in item.get(0, ''):
                resume_vals["first_name"] = item.get(1, '')
            elif 'ID No. / Passport' in item.get(0, ''):
                resume_vals["id_passport"] = item.get(1, '')
            elif 'Languages' in item.get(0, ''):
                resume_vals["languages"] = item.get(1, '')
        print(">>>...........................", resume_vals)
        # Initialize empty lists for dynamic data entries
        qualifications = []
        courses = []
        employment_history = []
        skills = []


        # Fetch Qualification Lines
        for i in range(len(extracted_data)):
            if extracted_data[i].get(0) == 'Qualification':
                for j in range(i + 1, len(extracted_data)):
                    qualification = extracted_data[j].get(0)
                    institution = extracted_data[j].get(2)
                    year = extracted_data[j].get(5)
                    print(">...................", extracted_data[j].get(2))

                    # Append the record if it's a valid qualification
                    if extracted_data[j].get(2) == 'Courses' or qualification == '':
                        break
                    qualifications.append({
                        'qualification': qualification,
                        'institute': institution,
                        'year': year
                    })
        resume_vals['qualification_ids'] = [(0, 0, qual) for qual in qualifications]
        print(">.....................extracted_data", extracted_data)


        # Fetch Courses Lines
        in_courses_section = False

        for entry in extracted_data:
            # Check for the start of the courses section
            if entry.get(0) == '' and entry.get(1) == '' and entry.get(
                    2) == 'Courses':
                in_courses_section = True
                continue  # Move to the next entry

            # Check for the header of the course name and institution
            if in_courses_section and entry.get(
                    1) == 'Course Name' and entry.get(4) == 'Institution':
                continue  # Skip this header row

            # If we are in the courses section, check for course entries
            if in_courses_section:
                course_name = entry.get(
                    0)  # Assuming course name is in column 0
                course_institution = entry.get(
                    3)  # Assuming institution is in column 3

                # Only append valid course entries
                if course_name and course_institution:  # Ensure we have valid course name and institution
                    courses.append({
                        'course': course_name.strip(),
                        'course_institute': course_institution.strip()
                    })

                # Stop if we reach a non-course section or empty entry
                if not course_name and not course_institution:
                    break  # Exit the loop if we hit empty course names or institutions
                elif entry.get(
                        0) == 'Skills Matrix':  # Additional check to stop at "Skills Matrix"
                    break

        resume_vals['course_ids'] = [(0, 0, course) for course in
                                     courses]

        # Fetch Employmnt History Lines
        in_employment_section = False
        current_employment = {}

        # Iterate through the extracted data to find the employment history section
        for entry in extracted_data:
            # Check for the start of the employment history section
            if entry.get(3) == 'Employment History':
                in_employment_section = True
                continue  # Move to the next entry

            if in_employment_section:
                if entry.get(0) == 'Company Name':
                    if current_employment:  # If we already have a current employment record, save it
                        employment_history.append(current_employment)
                    current_employment = {'emp_company_name': entry.get(
                        2).strip()}  # Start a new record
                elif entry.get(0) == 'Dates Employed':
                    current_employment['emp_date_employed'] = entry.get(2).strip()
                elif entry.get(0) == 'Position':
                    current_employment['emp_position'] = entry.get(2).strip()
                elif entry.get(0) == 'Duties:':
                    current_employment[
                        'emp_duties'] = ''  # Initialize duties as an empty string
                elif current_employment.get('duties') is not None:
                    if entry.get(0).startswith('-'):
                        duty_item = entry.get(0).strip()
                        current_employment[
                            'duties'] += f"<div>{duty_item}</div>"  # Add duties as HTML block elements

                # Save the last employment record if we reach an empty entry
                if entry.get(0) == '' and entry.get(1) == '' and entry.get(
                        2) == '':
                    if current_employment:
                        employment_history.append(current_employment)
                    break
        resume_vals['employment_history_ids'] = [(0, 0, emp_history) for emp_history in
                                                 employment_history]
        print(">>>................qual", resume_vals)
        print(">>>................courses", employment_history)

        # Fetch Skill lines
        in_skills_section = False

        for entry in extracted_data:
            # Check for the start of the skills matrix section
            if entry.get(0) == 'Skills Matrix':
                in_skills_section = True
                continue  # Move to the next entry

            # Check for the header of the skills matrix
            if in_skills_section:
                if entry.get(1) == 'Primary Skills' or (
                        entry.get(0) == '' and entry.get(1) == ''):
                    continue  # Skip header rows and empty rows

                # Extract skill data
                skill_name = entry.get(0)  # Skill name is in column 0
                skill_experience = entry.get(3)  # Experience is in column 3
                skill_level = entry.get(4)  # Level is in column 4

                # Only append valid skill entries
                if skill_name:  # Ensure we have a valid skill name
                    skills.append({
                        'skill': skill_name.strip(),
                        'skill_experience': skill_experience.strip() if skill_experience else None,
                        'skill_level': skill_level.strip() if skill_level else None
                    })

                # Stop if we reach an empty entry (indicating the end of relevant entries)
                if not skill_name and not skill_experience and not skill_level:
                    break
        resume_vals['skill_ids'] = [(0, 0, skill) for skill in
                                    skills]
        # # Parse courses
        # course_found = False
        # for item in extracted_data:
        #     if item == course_header:
        #         course_found = True
        #         continue
        #     if course_found and item.get(1):  # Ensure Institution field exists
        #         courses.append({
        #             'course': item.get(0),
        #             'course_institute': item.get(1)
        #         })
        #     elif item == employment_header:  # End of course section
        #         course_found = False
        #
        # # Parse employment history
        # employment_found = False
        # for item in extracted_data:
        #     if item == employment_header:
        #         employment_found = True
        #         employment_history.append({
        #             'emp_company_name': item.get(1),
        #             'emp_date_employed': next(
        #                 (i[1] for i in extracted_data if i.get(0) == 'Dates Employed'),
        #                 ''),
        #             'emp_position': next(
        #                 (i[1] for i in extracted_data if i.get(0) == 'Position'), ''),
        #             'emp_duties': next((i[0] for i in extracted_data if
        #                                 i.get(0, '').startswith('Duties')), '')
        #         })
        #     elif item == skill_header:  # End of employment section
        #         employment_found = False
        #
        # # Parse skills
        # skill_found = False
        # for item in extracted_data:
        #     if item == skill_header:
        #         skill_found = True
        #         continue
        #     if skill_found and item.get(1):  # Ensure Experience field exists
        #         skills.append({
        #             'skill': item.get(0),
        #             'skill_experience': item.get(1),
        #             'skill_level': item.get(2)
        #         })

        # Creating the record in hr.applicant.resume model
        # record = self.env['hr.applicant.resume'].create(resume_vals)