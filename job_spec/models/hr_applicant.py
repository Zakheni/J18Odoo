from odoo import models, fields, api, _
from odoo.exceptions import UserError
import rsaidnumber
from pypdf import PdfReader
import base64
import io



class Applicant(models.Model):
    _inherit = "hr.applicant"

    # related_applicant_id = fields.Many2one("hr.applicant", string="Related Applicant")
    citizenship = fields.Selection([
        ('SA', 'South Africa'),
        ('other', 'Other')
    ], string='Citizenship', default='other')
    nationality_id = fields.Many2one("res.country", string="Country of Nationality")
    id_no = fields.Char(string="Identification number")
    date_of_birth = fields.Date(string="Date of birth")
    passport = fields.Char(string="Passport")
    #more fields from Zakinfo development
    gender = fields.Selection([('M','Male'),('F','Female')])
    disability =  fields.Selection([('N','No'),('Y','Yes')])
    disability_type = fields.Text(string="Disability Type")
    criminal_record =  fields.Selection([('N','No'),('Y','Yes')])
    crime_info = fields.Text(string="Crime Information")
    mode_of_work =  fields.Selection([('ST','Onsite'),('OB','Remote'), ('both','Hybrid')])
    how_many_years_of_experience = fields.Char(string="How many years of experience")
    notice_period = fields.Text(string="Notice period")
    location = fields.Text(string="Location")

    tell_me_about_your_self = fields.Text(string="1. Tell me about yourself")
    when_can_you_start = fields.Text(string="2. When can you start")
    what_are_your_salary_expectations = fields.Text(string="3. After you have went through the job spec for this role, what are your salary expectations?")
    why_are_you_in_the_job_market_at_the_moment = fields.Text(string="4. Why are you in the job market at the moment")
    how_do_you_feel_about_counter_offer = fields.Text(string="5. How do you feel about counter offer")
    what_are_possibilities_of_counter_offer = fields.Text(string="6. If my client offers you this job,"
                                                             "what are the possibility of your current company to counter offer?")
    what_are_your_proudest_professional_achievements = fields.Text(string="7. What are your proudest professional achievements?")
    what_is_your_idea_work_environment = fields.Text(string="8. What's your ideal work environment?")
    #zakinfo developmemt team
    are_you_interviewing_with_other_companies = fields.Text(string="9. Are you interviewing with other companies")
    when_would_you_be_available_to_start_a_new_role = fields.Text(string="10. When would you be available to start a new role")

    # Experience and backgrund tab
    knowledge_areas = fields.Char(string='In what areas are you most knowledgeable?')
    strengths = fields.Char(string='What are your strengths?')
    best_work_environment = fields.Char(string='What kind of environment do you need to do your best work?')
    how_do_you_work_under_pressure = fields.Char(string='How do you work under pressure?')
    leadership_style = fields.Char(string='What\'s your leadership style?')
    leadership_example = fields.Char(string='Tell me about when you used leadership skills to get a job done.')
    typical_day = fields.Char(string='Describe a typical day at your current job.')
    career_accomplishments = fields.Char(
        string='Tell me about one of your most significant career accomplishments so far.')
    conflict_handling_with_colleague = fields.Char(
        string='Was there a time you didn\'t work well with a manager or colleague? If so, can you tell me how you handled the situation?')
    sample_work = fields.Char(string='Can you provide us with a sample of your work?')
    motivation = fields.Char(string='What motivates you?')
    next_job_expectations = fields.Char(string='What are you looking for in your next job?')
    other_expectations_with_new_job = fields.Char(string='Others you looking for in your next job?')
    others = fields.Char(string='Others')

    # Reference Check 1
    ref_1_reference_check_for = fields.Char(string='Reference check for')
    ref_1_referee_name = fields.Char(string='Referee Name and Surname')
    ref_1_company = fields.Char(string='Company')
    ref_1_contact_number = fields.Char(string='Contact number')
    ref_1_company_worked_with = fields.Char(string='You worked with him/her at which company?')
    ref_1_position_held = fields.Char(string='What was his/her position?')
    ref_1_duration_worked = fields.Char(string='How long did he/she work for you?')
    ref_1_placement_position = fields.Char(string='Am placing him/her for this position')
    ref_1_skills_for_role = fields.Char(string='What skills does he/she have to perform well in this role?')
    ref_1_greatest_strengths = fields.Char(string='What are his/her greatest strengths?')
    ref_1_area_of_development = fields.Char(string='What is his/her area of development?')
    ref_1_communication_skill = fields.Char(string='How was his/her communication skill?')
    ref_1_work_preference = fields.Selection([
        ('alone', 'Alone'),
        ('team', 'With a team')
    ], string='Does he/she work better alone or with a team?')
    ref_1_relationship_with_coworkers = fields.Char(
        string='How was his relationship with his coworkers and Management?')
    ref_1_biggest_accomplishment = fields.Char(
        string='What was one of his/her biggest accomplishments while you worked together?')
    ref_1_rating = fields.Integer(
        string='On a scale of 1 to 10, compared to other people you’ve hired, how would you rate him/her?')
    ref_1_reason_for_leaving = fields.Char(string='Why did he/she leave your company?')
    ref_1_rehire = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Would you rehire him/her?')
    ref_1_additional_comments = fields.Text(string='Is there any comment you would like to add?')

    # Reference Check 2
    ref_2_reference_check_for = fields.Char(string='Reference check for')
    ref_2_referee_name = fields.Char(string='Referee Name and Surname')
    ref_2_company = fields.Char(string='Company')
    ref_2_contact_number = fields.Char(string='Contact number')
    ref_2_company_worked_with = fields.Char(string='You worked with him/her at which company?')
    ref_2_position_held = fields.Char(string='What was his/her position?')
    ref_2_duration_worked = fields.Char(string='How long did he/she work for you?')
    ref_2_placement_position = fields.Char(string='Am placing him/her for this position')
    ref_2_skills_for_role = fields.Char(string='What skills does he/she have to perform well in this role?')
    ref_2_greatest_strengths = fields.Char(string='What are his/her greatest strengths?')
    ref_2_area_of_development = fields.Char(string='What is his/her area of development?')
    ref_2_communication_skill = fields.Char(string='How was his/her communication skill?')
    ref_2_work_preference = fields.Selection([
        ('alone', 'Alone'),
        ('team', 'With a team')
    ], string='Does he/she work better alone or with a team?')
    ref_2_relationship_with_coworkers = fields.Char(
        string='How was his relationship with his coworkers and Management?')
    ref_2_biggest_accomplishment = fields.Char(
        string='What was one of his/her biggest accomplishments while you worked together?')
    ref_2_rating = fields.Integer(
        string='On a scale of 1 to 10, compared to other people you’ve hired, how would you rate him/her?')
    ref_2_reason_for_leaving = fields.Char(string='Why did he/she leave your company?')
    ref_2_rehire = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Would you rehire him/her?')
    ref_2_additional_comments = fields.Text(string='Is there any comment you would like to add?')

    # Reference Check 3
    ref_3_reference_check_for = fields.Char(string='Reference check for')
    ref_3_referee_name = fields.Char(string='Referee Name and Surname')
    ref_3_company = fields.Char(string='Company')
    ref_3_contact_number = fields.Char(string='Contact number')
    ref_3_company_worked_with = fields.Char(string='You worked with him/her at which company?')
    ref_3_position_held = fields.Char(string='What was his/her position?')
    ref_3_duration_worked = fields.Char(string='How long did he/she work for you?')
    ref_3_placement_position = fields.Char(string='Am placing him/her for this position')
    ref_3_skills_for_role = fields.Char(string='What skills does he/she have to perform well in this role?')
    ref_3_greatest_strengths = fields.Char(string='What are his/her greatest strengths?')
    ref_3_area_of_development = fields.Char(string='What is his/her area of development?')
    ref_3_communication_skill = fields.Char(string='How was his/her communication skill?')
    ref_3_work_preference = fields.Selection([
        ('alone', 'Alone'),
        ('team', 'With a team')
    ], string='Does he/she work better alone or with a team?')
    ref_3_relationship_with_coworkers = fields.Char(
        string='How was his relationship with his coworkers and Management?')
    ref_3_biggest_accomplishment = fields.Char(
        string='What was one of his/her biggest accomplishments while you worked together?')
    ref_3_rating = fields.Integer(
        string='On a scale of 1 to 10, compared to other people you’ve hired, how would you rate him/her?')
    ref_3_reason_for_leaving = fields.Char(string='Why did he/she leave your company?')
    ref_3_rehire = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string='Would you rehire him/her?')
    ref_3_additional_comments = fields.Text(string='Is there any comment you would like to add?')

    candidate = fields.Char(string='Candidate')
    debrief_time = fields.Char(string='Debrief Time')
    debrief_date = fields.Date(string='Debrief Date')
    is_calendar_booked = fields.Boolean(string='Is the calendar booked for this meeting?')

    # Candidate Questions
    candidate_interview_experience = fields.Text(string='1. How do you think the interview went?')
    candidate_feelings_about_role = fields.Text(
        string='2. What are your feelings regarding the organization & the role now?')
    candidate_questions_asked = fields.Text(string='3. What type of questions did the hiring manager ask you?')
    candidate_own_questions = fields.Text(string='4. What questions did you ask at the end?')

    # Client Questions
    client_interview_experience = fields.Text(string='1. How did the interview go?')
    client_candidate_ability = fields.Text(string='2. Do you feel the candidate is able to handle the position?')
    client_candidate_strengths_weaknesses = fields.Text(
        string='3. What do you feel are the candidate’s strengths/weaknesses?')
    is_client_more_details_needed = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                 string='4. Are there any areas of their background where you would like more detail?')
    client_information_needed = fields.Text(string='5. If yes, what information would you like?')
    client_next_steps = fields.Text(string='6. How would you like to proceed from here?')
    client_offering_interview = fields.Text(
        string='7. Will the next meeting be an offering interview? If not, at what stage would you be making an offer?')

    salary_benefit_offer_in_line = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                    string='Is the salary and benefit offer in line with the candidate expectation?')
    clarified_counter_offer = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                               string='Did you clarify counter offer with the candidate?')
    did_candidate_accepted_offer = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                string='Did the candidate accept the offer?')
    # if_accepted_inactive_candidate = fields.Boolean(string='If yes, place the candidate on inactive and close the role')

    #zakinfo development team - client interview 
    how_do_you_think_the_interview_went = fields.Text(string="1. How do you think the interview went")
    #what_are_your_feelings_regarding_the_organization_and_the_role_now = fields.Text(string="2. What are your feelings regarding the organization & the role now")
    what_type_of_questions_did_the_hiring_manager_ask_you = fields.Text(string="2. What type of questions did the hiring manager ask you")
    what_questions_did_you_ask_at_the_end = fields.Text(string="3. What questions did you ask at the end")
    #zakinfo development team - offer stage
    #the_salary_and_benefit_offer_in_line_with_the_candidate_expectation = fields.Selection([('N','No'),('Y','Yes')])
    did_you_clarify_counter_offer_with_the_candidate = fields.Selection([('N','No'),('Y','Yes')])
    did_the_candidate_accept_the_offer = fields.Selection([('N','No'),('Y','Yes')])
    resume_copy = fields.Many2one('ir.attachment', string='Resume')
    zakheni_resume_id = fields.Many2one('hr.applicant.resume')
    is_create_resume_from_web = fields.Boolean()

    candidate_screening_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    consultant_interview_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    reference_check_1_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    reference_check_2_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    reference_check_3_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    cv_submitted_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    first_client_interview_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    second_client_interview_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )
    offer_stage = fields.Boolean(
        compute='_compute_stage_id', store=True,
    )

    f2f_interview_date = fields.Date()
    f2f_interview_time = fields.Char()
    f2f_interview_place = fields.Char()

    @api.depends('stage_id')
    def _compute_stage_id(self):
        for applicant in self:
            try:
                if applicant.stage_id == self.env.ref('job_spec.candidate_screen_stage_job'):
                    applicant.candidate_screening_stage = True
                else:
                    applicant.candidate_screening_stage = False
            except ValueError:
                applicant.candidate_screening_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.consultant_interview_stage_job'):
                    applicant.consultant_interview_stage = True
                else:
                    applicant.consultant_interview_stage = False
            except ValueError:
                applicant.consultant_interview_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.reference_check_1_stage_job'):
                    applicant.reference_check_1_stage = True
                    if not applicant.ref_1_reference_check_for:
                        applicant.ref_1_reference_check_for = applicant.partner_name
                    if not applicant.ref_2_reference_check_for:
                        applicant.ref_2_reference_check_for = applicant.partner_name
                    if not applicant.ref_3_reference_check_for:
                        applicant.ref_3_reference_check_for = applicant.partner_name
                else:
                    applicant.reference_check_1_stage = False
            except ValueError:
                applicant.reference_check_1_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.reference_check_2_stage_job'):
                    applicant.reference_check_2_stage = True
                else:
                    applicant.reference_check_2_stage = False
            except ValueError:
                applicant.reference_check_2_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.reference_check_3_stage_job'):
                    applicant.reference_check_3_stage = True
                else:
                    applicant.reference_check_3_stage = False
            except ValueError:
                applicant.reference_check_3_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.cv_submitted_stage_job'):
                    applicant.cv_submitted_stage = True
                else:
                    applicant.cv_submitted_stage = False
            except ValueError:
                applicant.cv_submitted_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.first_client_interview_stage_job'):
                    applicant.first_client_interview_stage = True
                else:
                    applicant.first_client_interview_stage = False
            except ValueError:
                applicant.first_client_interview_stage = False
            try:
                if applicant.stage_id == self.env.ref('job_spec.offer_stage_job'):
                    applicant.offer_stage = True
                else:
                    applicant.offer_stage = False
            except ValueError:
                applicant.offer_stage = False

    @api.model
    def create(self, vals):
        if vals.get('resume_copy'):
            resume_copy_val = vals.get('resume_copy')
            if isinstance(resume_copy_val, (list, tuple)):
                resume_copy_val = resume_copy_val[1]
            resume_wizard = self.env['import.resume'].create({'attachment_ids': [int(resume_copy_val)]})
            res = super(Applicant, self).create(vals)
            zakheni_resume_id = resume_wizard.with_context(applicant_id=res.id).import_resume()
            res.sudo().zakheni_resume_id = zakheni_resume_id
            return res

        return super(Applicant, self).create(vals)


    @api.onchange("nationality_id")
    def onchange_nationality_id(self):
        if self.nationality_id and self.nationality_id.id == self.env.ref('base.za').id:
            self.citizenship = 'SA'
        else:
            self.citizenship = 'other'

    @api.onchange("id_no")
    def onchange_id_no(self):
        if self.id_no:
            try:
                id_number = rsaidnumber.parse(self.id_no)
                if id_number.valid:
                    self.date_of_birth = id_number.date_of_birth.date()
            except Exception:
                raise UserError("Invalid Identification Number")
        else:
            self.date_of_birth = False

    # def name_get(self):
    #     if self.env.context.get('search_related_applicant'):
    #         result = []
    #         for record in self:
    #             name = ""
    #             if record.partner_name:
    #                 name = "{} [{}]".format(record.partner_name, record.name)
    #             result.append((record.id, name or record.name))
    #         return result
    #     return super(Applicant, self).name_get()

    @api.onchange("partner_name")
    def onchange_related_applicant_id(self):
        if self.partner_name:
            hr_applicant = self.search([('partner_name','=', self.partner_name)], limit=1)
            if hr_applicant:
                self.email_from = hr_applicant.email_from
                self.email_cc = hr_applicant.email_cc
                self.nationality_id = hr_applicant.nationality_id.id
                self.date_of_birth = hr_applicant.date_of_birth
                self.passport = hr_applicant.passport
                #Zakinfo development team
                self.gender = hr_applicant.gender
                self.disability = hr_applicant.disability
                self.criminal_record = hr_applicant.criminal_record
                self.mode_of_work = hr_applicant.mode_of_work
                self.how_many_years_of_experience = hr_applicant.how_many_years_of_experience
                self.notice_period = hr_applicant.notice_period
                self.location = hr_applicant.location

                #Zainfo development team
                self.partner_phone = hr_applicant.partner_phone
                # self.partner_mobile = hr_applicant.partner_mobile  # removed in Odoo 18
                self.linkedin_profile = hr_applicant.linkedin_profile
                self.type_id = hr_applicant.type_id.id
                self.interviewer_ids = [(6, 0, hr_applicant.interviewer_ids.ids)]
                # self.user_id = hr_applicant.user_id.id  # Uncomment if you want to assign user_id
                self.priority = hr_applicant.priority
                self.source_id = hr_applicant.source_id.id
                self.medium_id = hr_applicant.medium_id.id
                self.categ_ids = [(6, 0, hr_applicant.categ_ids.ids)]
                self.job_id = hr_applicant.job_id.id
                self.department_id = hr_applicant.department_id.id
                self.extract_remote_id = hr_applicant.extract_remote_id
                self.salary_expected = hr_applicant.salary_expected
                self.salary_proposed = hr_applicant.salary_proposed
                self.availability = hr_applicant.availability
                self.tell_me_about_your_self = hr_applicant.tell_me_about_your_self
                self.when_can_you_start = hr_applicant.when_can_you_start
                self.why_are_you_in_the_job_market_at_the_moment = hr_applicant.why_are_you_in_the_job_market_at_the_moment
                self.how_do_you_feel_about_counter_offer = hr_applicant.how_do_you_feel_about_counter_offer
                self.what_are_your_proudest_professional_achievements = hr_applicant.what_are_your_proudest_professional_achievements
                # zakinfo development team 
                self.are_you_interviewing_with_other_companies = hr_applicant.are_you_interviewing_with_other_companies
                self.when_would_you_be_available_to_start_a_new_role = hr_applicant.when_would_you_be_available_to_start_a_new_role
                #zainfo development team - reference check tab1
                try:
                    self.reference_Name_and_surname_1 = hr_applicant.reference_Name_and_surname_1
                    self.company_name_1 = hr_applicant.company_name_1
                    self.contact_number_1 = hr_applicant.contact_number_1
                except AttributeError:
                    pass
                #zainfo development team - reference check tab2
                try:
                    self.reference_Name_and_surname_2 = hr_applicant.reference_Name_and_surname_2
                    self.company_name_2 = hr_applicant.company_name_2
                    self.contact_number_2 = hr_applicant.contact_number_2
                except AttributeError:
                    pass
                #zainfo development team - reference check tab3
                try:
                    self.reference_Name_and_surname_3 = hr_applicant.reference_Name_and_surname_3
                    self.company_name_3 = hr_applicant.company_name_3
                    self.contact_number_3 = hr_applicant.contact_number_3
                except AttributeError:
                    pass
                #zakinfo development team - client interview 
                self.how_do_you_think_the_interview_went = hr_applicant.how_do_you_think_the_interview_went
                #self.what_are_your_feelings_regarding_the_organization_and_the_role_now = hr_applicant.what_are_your_feelings_regarding_the_organization_and_the_role_now
                self.what_type_of_questions_did_the_hiring_manager_ask_you = hr_applicant.what_type_of_questions_did_the_hiring_manager_ask_you
                self.what_questions_did_you_ask_at_the_end = hr_applicant.what_questions_did_you_ask_at_the_end
                #zakinfo development team - offer Stage
                #self.the_salary_and_benefit_offer_in_line_with_the_candidate_expectation = hr_applicant.the_salary_and_benefit_offer_in_line_with_the_candidate_expectation
                self.did_you_clarify_counter_offer_with_the_candidate = hr_applicant.did_you_clarify_counter_offer_with_the_candidate
                self.did_the_candidate_accept_the_offer = hr_applicant.did_the_candidate_accept_the_offer

                #             })



class RecruitmentStages(models.Model):
    _inherit='hr.recruitment.stage'

    def update_recruitment_stages(self):
        test_job = self.env['hr.job'].search([('name', '=', 'Test')])
        if not test_job:
            test_job = self.env['hr.job'].create({'name': 'Test'})
        for rec in self:
            rec['job_ids'] = test_job.ids
