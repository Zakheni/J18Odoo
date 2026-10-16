# -*- coding: utf-8 -*-
import base64
import os
import shutil
import threading
import time

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.addons.cv_studio.services import engine


class CvPack(models.Model):
    _name = "cv.pack"
    _description = "CV Pack"
    _order = "create_date desc"

    name = fields.Char(required=True, default="New CV Pack")
    state = fields.Selection(
        [("new", "New"), ("parsed", "Parsed"), ("drafted", "Drafted"), ("built", "Built")],
        default="new", readonly=True, copy=False)
    engine_id = fields.Char("Engine ID", readonly=True, copy=False,
                            help="Identifier of this pack's scratch working directory.")

    input_file = fields.Binary("Pack (zip)")
    input_filename = fields.Char()
    input_token = fields.Char(
        "Upload Token", readonly=True, copy=False,
        help="Reference to a pack zip streamed to the server by the dropzone.")
    source_path = fields.Char(
        "Server Folder", help="Alternatively, a folder path on the server to ingest.")

    log = fields.Text(readonly=True, copy=False)
    dest_path = fields.Char("Destination Folder",
                            help="Optional: also copy the finished CVs here.")
    deploy_to_dest = fields.Boolean("Copy finished CVs to a folder on this PC",
                                    default=True)

    candidate_ids = fields.One2many("cv.candidate", "pack_id")
    candidate_count = fields.Integer(compute="_compute_counts")
    drafted_count = fields.Integer(compute="_compute_counts")
    draft_failed = fields.Char(readonly=True, copy=False)

    # ------------------------------------------------------------ config
    def _param(self, key, default=None):
        return self.env["ir.config_parameter"].sudo().get_param(key, default)

    def _apply_engine_config(self):
        work_root = self._param("cv_studio.work_root") or None
        dest_root = self._param("cv_studio.dest_root") or None
        engine.configure(
            work_root=work_root,
            dest_root=dest_root,
            opencode_exe=self._param("cv_studio.opencode_exe"),
            model=self._param("cv_studio.model"),
        )

    def _get_model(self):
        return self._param("cv_studio.model", engine.DEFAULT_MODEL)

    def _get_timeout(self):
        try:
            return int(self._param("cv_studio.timeout", "300"))
        except (TypeError, ValueError):
            return 300

    def _get_max_chars(self):
        try:
            return int(self._param("cv_studio.max_chars", "20000"))
        except (TypeError, ValueError):
            return 20000

    def _work_dir(self):
        return engine.cv_std.work_dir(self.engine_id)

    def _new_build_dir(self):
        d = os.path.join(self._work_dir(), "build_%s" % time.strftime("%Y%m%d_%H%M%S"))
        os.makedirs(d, exist_ok=True)
        return d

    # ------------------------------------------------------------ computes
    @api.depends("candidate_ids", "candidate_ids.draft_state")
    def _compute_counts(self):
        for pack in self:
            pack.candidate_count = len(pack.candidate_ids)
            pack.drafted_count = len(pack.candidate_ids.filtered(
                lambda c: c.draft_state == "drafted"))

    def _log(self, msg):
        stamp = time.strftime("%H:%M:%S")
        self.log = (self.log or "") + "[%s] %s\n" % (stamp, msg)
        try:
            self.env.cr.commit()
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------ parse
    def action_parse(self):
        self.ensure_one()
        self._apply_engine_config()
        engine_id = self.engine_id or ("odoo_pack_%s" % self.id)
        self.engine_id = engine_id
        input_path = self._resolve_input()
        self._log("Parsing pack from %s" % input_path)
        mf = engine.cv_std.unpack(input_path, engine_id)
        self.candidate_ids.unlink()
        seq = 10
        for c in mf["candidates"]:
            self.env["cv.candidate"].create({
                "pack_id": self.id,
                "key": c["key"],
                "name": c["name"],
                "role": c.get("role") or False,
                "target_role": c.get("role") or False,
                "sequence": seq,
                "source_cvs": "\n".join(cv["base"] for cv in c.get("cvs", [])),
                "source_docs": "\n".join(d["base"] for d in c.get("docs", [])),
            })
            seq += 10
        self.state = "parsed"
        self._log("Parsed %d candidates" % len(mf["candidates"]))
        return True

    @api.model
    def _uploads_dir(self):
        return os.path.join(engine.cv_std.ROOT_TEMP, "_uploads")

    def _resolve_input(self):
        if self.input_token:
            updir = self._uploads_dir()
            found = None
            if os.path.isdir(updir):
                prefix = self.input_token + "."
                for name in sorted(os.listdir(updir)):
                    if name.startswith(prefix):
                        found = os.path.join(updir, name)
                        break
            if not found:
                raise UserError(_(
                    "The uploaded file is no longer available on the server. "
                    "Please upload the pack again."))
            return found
        if self.input_file:
            updir = self._uploads_dir()
            os.makedirs(updir, exist_ok=True)
            zpath = os.path.join(updir, self.input_filename or ("%s.zip" % self.id))
            with open(zpath, "wb") as fh:
                fh.write(base64.b64decode(self.input_file))
            return zpath
        if self.source_path and os.path.exists(self.source_path):
            return self.source_path
        raise UserError(_("Upload a pack zip, or set a valid server folder path."))

    def action_reextract(self):
        self.ensure_one()
        self._apply_engine_config()
        res = engine.cv_std.reextract(self.engine_id)
        self._log("Re-extracted text for %s files" % res.get("reextracted"))
        return True

    # ------------------------------------------------------------ draft
    def action_draft_fast(self):
        self.ensure_one()
        self._apply_engine_config()
        for cand in self.candidate_ids:
            cand._draft(llm=False)
        self._log("Fast-drafted %d candidates" % len(self.candidate_ids))
        self.state = "drafted"
        return True

    def action_draft_ai(self):
        self.ensure_one()
        self._apply_engine_config()
        self.draft_failed = False
        self._log("AI draft started (model %s)" % self._get_model())
        t = threading.Thread(target=self._ai_draft_thread, daemon=True)
        t.start()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"type": "info", "title": _("AI Draft Started"),
                       "message": _("Drafting runs in the background; refresh the pack to see progress."),
                       "sticky": False},
        }

    def _ai_draft_thread(self):
        registry = self.env.registry
        dbname = self.env.cr.dbname
        pack_id = self.id
        try:
            with registry.cursor() as cr:
                env = api.Environment(cr, self.env.uid, {})
                pack = env["cv.pack"].browse(pack_id)
                pack._apply_engine_config()
                done = 0
                for cand in pack.candidate_ids:
                    try:
                        cand._draft(llm=True)
                        done += 1
                        pack._log("Drafted %s (%d/%d)" % (cand.name, done, len(pack.candidate_ids)))
                    except Exception as e:  # noqa: BLE001
                        cand.weak = "error: %s" % e
                        pack._log("FAILED %s: %s" % (cand.name, e))
                pack.state = "drafted"
                pack._log("AI draft finished: %d candidates" % done)
                cr.commit()
        except Exception as e:  # noqa: BLE001
            try:
                with registry.cursor() as cr:
                    env = api.Environment(cr, self.env.uid, {})
                    pack = env["cv.pack"].browse(pack_id)
                    pack.draft_failed = str(e)
                    pack._log("AI draft aborted: %s" % e)
                    cr.commit()
            except Exception:
                pass

    # ------------------------------------------------------------ build
    def _default_output_root(self):
        return os.path.join(os.path.expanduser("~"), "Downloads", "CV Studio")

    def _dest_root(self):
        if self.dest_path:
            return self.dest_path
        root = self._param("cv_studio.dest_root") or self._default_output_root()
        return os.path.join(root, self.name or "CV Pack")

    def action_build(self):
        self.ensure_one()
        self._apply_engine_config()
        outdir = self._new_build_dir()
        self._log("Generating CVs into %s" % outdir)
        for cand in self.candidate_ids:
            cand._build_docx(outdir)
        engine.pdf_conv.convert(outdir, outdir)
        deployed = 0
        dest_root = self._dest_root()
        for cand in self.candidate_ids:
            cand._attach_outputs(outdir)
            if self.deploy_to_dest:
                deployed += self._deploy_candidate(cand, outdir, dest_root)
        self.state = "built"
        msg = "Built %d CVs" % len(self.candidate_ids)
        if self.deploy_to_dest:
            msg += "; copied to %s" % dest_root
        self._log(msg)
        return True

    def _deploy_candidate(self, cand, outdir, dest_root):
        role = (cand.role or "").strip()
        dst = os.path.join(dest_root, role, cand.name) if role \
            else os.path.join(dest_root, cand.name)
        os.makedirs(dst, exist_ok=True)
        base = engine.gen_cv.to_filename(cand.name)
        n = 0
        for f in (base + ".docx", base + ".pdf"):
            src = os.path.join(outdir, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(dst, f))
                n += 1
        import re
        for line in (cand.docs or "").splitlines():
            m = re.search(r"\(see: (.+)\)", line)
            if not m:
                continue
            fname = m.group(1).strip()
            src = engine.cv_std.resolve_doc_path(self.engine_id, fname)
            if src and os.path.exists(src):
                shutil.copy2(src, os.path.join(dst, fname))
                n += 1
        return n

    # ------------------------------------------------------------ download
    def action_download_all(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/cv_studio/download/pack/%d/zip" % self.id,
            "target": "self",
        }

    # ------------------------------------------------------------ views
    def action_view_candidates(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Candidates"),
            "res_model": "cv.candidate",
            "view_mode": "list,form",
            "domain": [("pack_id", "=", self.id)],
            "context": {"default_pack_id": self.id},
        }
