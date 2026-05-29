from pypdf import PdfReader
import base64
import io

from odoo import models, fields, api, _
import re



class ImportResume(models.TransientModel):
    _name = 'import.resume'
    _description = 'Zakheni Resume Import'

    resume = fields.Binary("Upload Resume")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    def import_resume(self):
        for resume in self.attachment_ids:
            pdf_data = base64.b64decode(resume.datas)
            reader = PdfReader(io.BytesIO(pdf_data))
            values = {}
            skill_summary = ''
            for page in reader.pages:
                resume_content = page.extract_text()

                lines = resume_content.split('\n')
                last_name = first_name = None
                nationality = languages = None
                qualification_lines = []
                employment_history_lines = []

                # Search for last name and first name
                for line in lines:
                    if 'Last Name:' in line:
                        last_name = line.split(':')[-1].strip()
                    elif 'First Name:' in line or 'name' in line:
                        first_name = line.split(':')[-1].strip()
                    elif 'Nationality:' in line:
                        nationality = line.split(':')[-1].strip()
                    elif 'Language' in line:
                        languages = line.split(':')[-1].strip()

                # Extract Skills summary
                lines = resume_content.split('\n')
                start_index = -1
                for i, line in enumerate(lines):
                    if "Skill" in line or "SKILLS" in line:
                        start_index = i
                        break
                end_index = -1
                for i, line in enumerate(lines):
                    if "PROJECTS" in line or "Experience" in line or "Education" in line:
                        end_index = i
                        break
                if start_index != -1 and end_index != -1:
                    skills_content = lines[start_index + 1:end_index]
                    skill_summary = "\n".join(skills_content)
                # Extract qualifications
                qualifications_pattern = re.compile(
                    r'EDUCATION & QUALIFICATIONS\s+(.*?)(?:PROFESSIONAL EXPERIENCE|PROJECTS)', re.DOTALL)
                qualifications_match = qualifications_pattern.search(resume_content)
                if qualifications_match:
                    qualifications = qualifications_match.group(1).strip()
                    qualification_lines = self.get_qualification_lines(qualifications)

                # Extract Employment History
                employment_history_pattern = re.compile(r"PROFESSIONAL EXPERIENCE(.+?)SKILLS", re.DOTALL)
                employment_history_match = employment_history_pattern.search(resume_content)
                if employment_history_match:
                    experience_section = employment_history_match.group(1).strip()
                    job_experiences = re.split(r"_{5,}", experience_section)

                    employment_history = self.prepare_job_experience_data(job_experiences)

                    employment_history_lines = []

                    for entry in employment_history:
                        company_date, position, duties = entry
                        company_name, date_employed = company_date.split(maxsplit=1)

                        employment_history_lines.append((0, 0, {
                            'emp_company_name': company_name.strip(),
                            'emp_date_employed': date_employed.strip(),
                            'emp_position': position.strip(),
                            'emp_duties': duties.strip()
                        }))

                # Extract references
                reference_lines = self.prepare_job_reference_data(resume_content)
                if self.env.context.get('applicant_id'):
                    values.update({'applicant_id': int(self.env.context.get('applicant_id'))})
                values.update({'surname': last_name,
                               'first_name': first_name,
                               'id_passport': nationality,
                               'languages': languages,
                               'qualification_ids': qualification_lines,
                               'skills_summary': skill_summary,
                               'employment_history_ids': employment_history_lines,
                               'reference_ids': reference_lines})
            zakheni_resume = self.env['hr.applicant.resume'].create(values)
            return zakheni_resume.id

    def get_qualification_lines(self, qualification_string):

        pattern = r"(\b\w{4}\b)\s+(\w+\s+\w+\s+\w+)\s+(.+)"
        # pattern = r'(\d{4})\s+(.+?)\s+(.+)'

        # Find all matches in the text using the pattern
        matches = re.findall(pattern, qualification_string)

        # Create a list of dictionaries for one2many creation
        qualification_lines = []
        for match in matches:
            year, institute, qualification = match

            qualification_lines.append((0,0,{
                'year': year,
                'institute': institute.strip(),
                'qualification': qualification.strip()
            }))
        return qualification_lines

    def prepare_job_experience_data(self, job_experiences):
        employment_history = []
        for job_experience in job_experiences:
            job_lines = job_experience.strip().split("\n")
            if len(job_lines) >= 2:
                # Extract company and duration
                company_duration_line = job_lines[0].strip()
                company_duration_parts = company_duration_line.split("-")
                if len(company_duration_parts) >= 2:
                    company = company_duration_parts[0].strip()
                    duration = company_duration_parts[1].strip()
                    job_description = "\n".join(job_lines[1:]).strip()
                    employment_history.append((company, duration, job_description))
        return employment_history

    def prepare_job_reference_data(self, resume_content):
        references = []
        lines = resume_content.split('\n')

        company = ""
        person = ""
        person_contact = ""

        for line in lines:
            if "Reference" in line:
                index = lines.index(line)
                for i in range(index + 1, len(lines)):
                    if "Name:" in lines[i]:
                        person = lines[i].split(":")[1].strip()
                    elif "Place:" in lines[i]:
                        company = lines[i].split(":")[1].strip()
                    elif "Cell:" in lines[i]:
                        person_contact = lines[i].split(":")[1].strip()
                    elif "PROJECTS WORKED ON AT" in lines[i]:
                        break
        references.append((0, 0, {
            'ref_company': company,
            'ref_person': person,
            'ref_person_contact_details': person_contact
        }))
        return references