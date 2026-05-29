# Copyright 2017-2019 MuK IT GmbH.
# Copyright 2020 Creu Blanca
# Copyright 2021 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError

_logger = logging.getLogger(__name__)


class Storage(models.Model):
    _name = "dms.storage"
    _description = "Storage"

    name = fields.Char(required=True)
    save_type = fields.Selection(
        selection=[
            ("database", "Database"),
            ("file", "Filestore"),
            ("local", "Local Filesystem"),
            ("sharepoint", "SharePoint"),
            ("attachment", "Attachment"),
        ],
        default="database",
        required=True,
        help="The save type is used to determine how a file is saved by the system. "
        "If you change this setting, you can migrate existing files manually by "
        "triggering the action.",
    )
    local_storage_path = fields.Char(
        string="Local Storage Path",
        help="Absolute path to the local directory where files will be stored. "
        "Only used when save type is 'Local Filesystem'.",
    )
    sharepoint_site_id = fields.Integer(
        string="SharePoint Site ID",
        help="SharePoint site ID. Only used when save type is 'SharePoint'.",
    )
    sharepoint_library_name = fields.Char(
        string="SharePoint Library Name",
        help="Name of the SharePoint document library. Only used when save type is 'SharePoint'.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        help="If set, directories and files will only be available for "
        "the selected company.",
    )
    is_hidden = fields.Boolean(
        string="Storage is Hidden",
        default=False,
        help="Indicates if directories and files are hidden by default.",
    )
    root_directory_ids = fields.One2many(
        comodel_name="dms.directory",
        inverse_name="storage_id",
        string="Root Directories",
        auto_join=False,
        readonly=False,
        copy=False,
    )
    storage_directory_ids = fields.One2many(
        comodel_name="dms.directory",
        inverse_name="storage_id",
        string="Directories",
        auto_join=False,
        readonly=True,
        copy=False,
    )
    storage_file_ids = fields.One2many(
        comodel_name="dms.file",
        inverse_name="storage_id",
        string="Files",
        auto_join=False,
        readonly=True,
        copy=False,
    )
    count_storage_directories = fields.Integer(
        compute="_compute_count_storage_directories", string="Count Directories"
    )
    count_storage_files = fields.Integer(
        compute="_compute_count_storage_files", string="Count Files"
    )
    model_ids = fields.Many2many("ir.model", string="Linked Models")
    inherit_access_from_parent_record = fields.Boolean(
        string="Inherit permissions from related record",
        default=False,
        help="Indicate if directories and files access work only with "
        "related model access (for example, if some directories are related "
        "with any sale, only users with read access to these sale can access)",
    )
    include_message_attachments = fields.Boolean(
        string="Create files from message attachments",
        default=False,
        help="Indicate if directories and files auto-create in mail "
        "composition process too",
    )
    model = fields.Char(search="_search_model", store=False)

    def _search_model(self, operator, value):
        allowed_items = self.env["ir.model"].sudo().search([("model", operator, value)])
        return [("model_ids", "in", allowed_items.ids)]

    @api.onchange("save_type")
    def _onchange_save_type(self):
        for record in self:
            if record.save_type == "attachment":
                record.inherit_access_from_parent_record = True

    def _get_sharepoint_client(self):
        self.ensure_one()
        if not self.sharepoint_site_id:
            return None
        try:
            site = self.env["sharepoint.site"].browse(self.sharepoint_site_id)
            if site.exists():
                return site._get_client()
        except KeyError:
            _logger.warning("sharepoint.site model not available. sharepoint_connector may not be installed.")
        except Exception:
            _logger.warning("Error getting SharePoint client", exc_info=True)
        return None

    # Actions
    def action_storage_migrate(self):
        if self.save_type != "attachment":
            if not self.env.user.has_group("dms.group_dms_manager"):
                raise AccessError(_("Only managers can execute this action."))
            files = self.env["dms.file"].with_context(active_test=False).sudo()

            for record in self:
                domain = [
                    ("require_migration", "=", True),
                    ("storage_id", "=", record.id),
                ]
                files.search(domain).action_migrate()

    def action_save_onboarding_storage_step(self):
        self.env.user.company_id.set_onboarding_step_done(
            "documents_onboarding_storage_state"
        )

    # Read, View
    @api.depends("storage_directory_ids")
    def _compute_count_storage_directories(self):
        for record in self:
            record.count_storage_directories = len(record.storage_directory_ids)

    @api.depends("storage_file_ids")
    def _compute_count_storage_files(self):
        for record in self:
            record.count_storage_files = len(record.storage_file_ids)

    @api.constrains("save_type", "local_storage_path", "sharepoint_site_id", "sharepoint_library_name")
    def _check_storage_config(self):
        for record in self:
            if record.save_type == "local" and not record.local_storage_path:
                raise ValidationError(
                    _("Local storage path is required when save type is 'Local Filesystem'.")
                )
            if record.save_type == "sharepoint" and not record.sharepoint_site_id:
                raise ValidationError(
                    _("SharePoint site is required when save type is 'SharePoint'.")
                )
            if record.save_type == "sharepoint" and not record.sharepoint_library_name:
                raise ValidationError(
                    _("SharePoint library name is required when save type is 'SharePoint'.")
                )

    def write(self, values):
        res = super().write(values)
        if "model_ids" in values:
            self.env.registry.clear_cache()
        return res
