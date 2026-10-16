# -*- coding: utf-8 -*-
from odoo import fields, models


class CvCompetency(models.Model):
    _name = "cv.competency"
    _description = "CV Competency"
    _order = "sequence, id"

    candidate_id = fields.Many2one("cv.candidate", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    label = fields.Char("Label")
    text = fields.Char("Description")


class CvCert(models.Model):
    _name = "cv.cert"
    _description = "CV Certification"
    _order = "sequence, id"

    candidate_id = fields.Many2one("cv.candidate", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char("Certification", required=True)


class CvEducation(models.Model):
    _name = "cv.education"
    _description = "CV Education"
    _order = "sequence, id"

    candidate_id = fields.Many2one("cv.candidate", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    institution = fields.Char("Institution")
    qual = fields.Char("Qualification")
    dates = fields.Char("Dates")


class CvCareer(models.Model):
    _name = "cv.career"
    _description = "CV Employment"
    _order = "sequence, id"

    candidate_id = fields.Many2one("cv.candidate", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    company = fields.Char("Company")
    title = fields.Char("Job Title")
    dates = fields.Char("Dates")
    bullets = fields.Text("Responsibilities", help="One achievement per line.")
