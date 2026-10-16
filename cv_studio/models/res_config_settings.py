# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    cv_studio_work_root = fields.Char(
        "Work Folder", config_parameter="cv_studio.work_root",
        help="Where pack working files are kept. Blank uses the engine default.")
    cv_studio_dest_root = fields.Char(
        "Output Folder", config_parameter="cv_studio.dest_root",
        help="Folder on this PC where finished CVs are copied. Each pack gets a "
             "subfolder named after the pack. Blank uses "
             "<user>\\Downloads\\CV Studio")
    cv_studio_opencode_exe = fields.Char(
        "opencode Executable", config_parameter="cv_studio.opencode_exe")
    cv_studio_model = fields.Char(
        "AI Model", config_parameter="cv_studio.model", default="opencode/big-pickle")
    cv_studio_max_chars = fields.Integer(
        "Max CV Characters", config_parameter="cv_studio.max_chars", default=20000,
        help="Longest CV text sent to the AI (head and tail are kept).")
    cv_studio_timeout = fields.Integer(
        "AI Timeout (s)", config_parameter="cv_studio.timeout", default=300)
