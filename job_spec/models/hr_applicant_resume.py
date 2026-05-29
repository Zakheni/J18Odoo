import json
from odoo import models, fields, api, _

class HRApplicantResume(models.Model):
    _name = 'hr.applicant.resume'
    _rec_name = 'display_name'
    _description = 'Zakheni Resume'

    display_name = fields.Char()
    applicant_id = fields.Many2one("hr.applicant")
    surname = fields.Char(string='Surname')
    first_name = fields.Char(string='First Name')
    position = fields.Char(string='Position')
    id_passport = fields.Char(string='ID/Passport')
    email = fields.Char(related='applicant_id.email_from')
    languages = fields.Char(string='Languages')
    qualification_ids = fields.One2many('applicant.qualification', 'resume_id', string="Qualifications")
    executive_summary = fields.Text(string='Executive Summary')
    skills_summary = fields.Text(string='Skills summary')
    additional_comments = fields.Text(string='Additional Comments')
    course_ids = fields.One2many('applicant.course', 'resume_id', string="Courses")
    employment_history_ids = fields.One2many('applicant.employment.history', 'resume_id', string="Employment History")
    skill_ids = fields.One2many('applicant.skill', 'resume_id', string="Skills")
    reference_ids = fields.One2many('applicant.reference', 'resume_id', string="References")


    @api.model
    def create(self, vals):
        resume = super(HRApplicantResume, self).create(vals)
        if resume.first_name and resume.surname and resume.applicant_id:
            resume.display_name = resume.first_name + ' ' + resume.surname + ' - ' + resume.applicant_id.name.split('-')[1] if len(resume.applicant_id.name.split('-')) > 0 else ''
        elif resume.first_name and resume.surname and resume.position:
            resume.display_name = resume.first_name + ' ' + resume.surname + ' ' + resume.position
        else:
            pass
        return resume

    def write(self, vals):
        if vals.get('first_name') and vals.get('surname') and vals.get('applicant_id'):
            applicant_id = self.env['hr.applicant'].sudo().browse(int(self.applicant_id))
            vals['display_name'] = vals.get('first_name') + ' ' + vals.get('surname') + ' - ' + \
                                applicant_id.name.split('-')[1] if len(
                applicant_id.name.split('-')) > 0 else ''
        elif vals.get('first_name') and vals.get('surname') and vals.get('position'):
            vals['display_name'] = vals.get('first_name') + ' ' + vals.get('surname') + ' ' + vals.get('position')
        else:
            pass
        res = super(HRApplicantResume, self).write(vals)
        return res


class ApplicantQualification(models.Model):
    _name = 'applicant.qualification'
    _rec_name = 'qualification'

    resume_id = fields.Many2one("hr.applicant.resume")
    qualification = fields.Char("Qualification")
    institute = fields.Char("Institution")
    year = fields.Integer("year")

class ApplicantCourse(models.Model):
    _name = 'applicant.course'
    _rec_name = 'course'

    resume_id = fields.Many2one("hr.applicant.resume")
    course = fields.Char("Course Name")
    course_institute = fields.Char("Institution")

class ApplicantEmploymentHistory(models.Model):
    _name = 'applicant.employment.history'
    _rec_name = 'emp_company_name'

    resume_id = fields.Many2one("hr.applicant.resume")
    emp_company_name = fields.Char("Company")
    emp_date_employed = fields.Char("Employed Dates")
    emp_position = fields.Char("Position")
    emp_duties = fields.Html("Emp Duties")

class ApplicantSkill(models.Model):
    _name = 'applicant.skill'
    _rec_name = 'skill'

    resume_id = fields.Many2one("hr.applicant.resume")
    skill = fields.Char("Skill")
    skill_experience = fields.Char("skill_experience")
    skill_level = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3')
    ], string="Level (1 = Beginner, 2 = Advanced, 3 = Expert)")

class ApplicantReference(models.Model):
    _name = 'applicant.reference'
    _rec_name = 'ref_company'

    resume_id = fields.Many2one("hr.applicant.resume")
    ref_company = fields.Char("Company")
    ref_person = fields.Char("Contact Person")
    ref_person_contact_details = fields.Char("Contact Details")
