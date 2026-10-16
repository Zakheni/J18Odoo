# -*- coding: utf-8 -*-
import base64
import os
import re

from odoo import api, fields, models
from odoo.addons.cv_studio.services import engine


class CvCandidate(models.Model):
    _name = "cv.candidate"
    _description = "CV Candidate"
    _order = "pack_id, sequence, name"

    pack_id = fields.Many2one("cv.pack", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    key = fields.Char("Key")
    name = fields.Char(required=True)
    role = fields.Char()
    target_role = fields.Char("Target Role")

    summary = fields.Text(help="One paragraph per line; prefix a line with '- ' for a bullet.")
    competency_ids = fields.One2many("cv.competency", "candidate_id")
    cert_ids = fields.One2many("cv.cert", "candidate_id")
    education_ids = fields.One2many("cv.education", "candidate_id")
    career_ids = fields.One2many("cv.career", "candidate_id")
    refs = fields.Text(help="One referee per line.")
    docs = fields.Text(help="One supporting document per line, each ending '(see: <filename>)'.")

    weak = fields.Char("Weak Draft", readonly=True,
                       help="If set, the draft is unreliable (e.g. no usable CV text).")
    draft_state = fields.Selection(
        [("todo", "To Draft"), ("drafted", "Drafted"), ("failed", "Draft Failed")],
        default="todo")
    source_cvs = fields.Text("Source CVs", readonly=True)
    source_docs = fields.Text("Source Documents", readonly=True)

    output_docx = fields.Binary("CV (DOCX)", readonly=True, attachment=False)
    output_docx_name = fields.Char()
    output_pdf = fields.Binary("CV (PDF)", readonly=True, attachment=False)
    output_pdf_name = fields.Char()

    # ------------------------------------------------------------ conversion
    def to_dict(self):
        self.ensure_one()
        return {
            "name": self.name or "",
            "role": self.role or "",
            "target_role": self.target_role or "",
            "summary": [ln for ln in (self.summary or "").splitlines() if ln.strip()],
            "competencies": [[c.label or "", c.text or ""] for c in self.competency_ids],
            "certs": [c.name for c in self.cert_ids if c.name],
            "education": [{"institution": e.institution or "", "qual": e.qual or "",
                           "dates": e.dates or ""} for e in self.education_ids],
            "career": [{"company": j.company or "", "title": j.title or "",
                        "dates": j.dates or "",
                        "bullets": [b for b in (j.bullets or "").splitlines() if b.strip()]}
                       for j in self.career_ids],
            "refs": [ln for ln in (self.refs or "").splitlines() if ln.strip()],
            "docs": [ln for ln in (self.docs or "").splitlines() if ln.strip()],
        }

    def apply_dict(self, d):
        self.ensure_one()
        self.write({
            "name": d.get("name") or self.name,
            "role": d.get("role") or self.role,
            "target_role": d.get("target_role") or d.get("role") or self.target_role,
            "summary": "\n".join(d.get("summary") or []),
            "refs": "\n".join(d.get("refs") or []),
            "docs": "\n".join(d.get("docs") or []),
        })
        self._replace_lines("competency_ids", [
            {"label": c[0], "text": c[1]} for c in (d.get("competencies") or []) if c])
        self._replace_lines("cert_ids", [
            {"name": c} for c in (d.get("certs") or []) if c])
        self._replace_lines("education_ids", [
            {"institution": e.get("institution"), "qual": e.get("qual"),
             "dates": e.get("dates")} for e in (d.get("education") or [])])
        self._replace_lines("career_ids", [
            {"company": j.get("company"), "title": j.get("title"),
             "dates": j.get("dates"), "bullets": "\n".join(j.get("bullets") or [])}
            for j in (d.get("career") or [])])
        self.weak = d.get("_weak") or False

    def _replace_lines(self, field, vals_list):
        cmds = [(5, 0, 0)]
        for i, vals in enumerate(vals_list):
            vals = dict(vals)
            vals["sequence"] = (i + 1) * 10
            cmds.append((0, 0, vals))
        self.write({field: cmds})

    # ------------------------------------------------------------ drafting
    def action_draft_fast(self):
        for cand in self:
            cand.pack_id._apply_engine_config()
            cand._draft(llm=False)
        return True

    def action_draft_ai(self):
        for cand in self:
            cand.pack_id._apply_engine_config()
            cand._draft(llm=True)
        return True

    def _draft(self, llm=False):
        self.ensure_one()
        pack = self.pack_id
        manifest = engine.cv_std.load_manifest(pack.engine_id)
        mc = self._manifest_candidate(manifest)
        docs = mc.get("docs", []) if mc else []
        cv_path = engine.cv_std.primary_cv_path(pack.engine_id, mc or {}, cvs_only=True) if mc else None
        has_cv = bool(cv_path) and os.path.getsize(cv_path) >= 1500
        got = None
        weak = None
        if llm and has_cv:
            for _ in range(2):
                try:
                    got = engine.llm_draft.draft_via_llm(
                        cv_path, name=self.name, role=self.role or "", docs=docs,
                        model=pack._get_model(), timeout=pack._get_timeout(),
                        max_chars=pack._get_max_chars())
                    break
                except Exception:  # noqa: BLE001
                    got = None
        if got is None:
            text = engine.cv_std.primary_cv_text(pack.engine_id, mc or {}) if mc else ""
            got = engine.autodraft.draft_from_text(
                text, name=self.name, role=self.role or "", docs=docs)
            if not has_cv:
                weak = "no usable CV text (scanned or image CV)"
            elif llm:
                weak = "AI draft failed; fast draft used"
        self.apply_dict(got)
        self.weak = weak
        self.draft_state = "drafted"
        return True

    def _manifest_candidate(self, manifest):
        for c in manifest.get("candidates", []):
            if c.get("key") == self.key:
                return c
        return None

    # ------------------------------------------------------------ generate
    def action_generate(self):
        for cand in self:
            cand.pack_id._apply_engine_config()
            outdir = cand.pack_id._new_build_dir()
            cand._build_docx(outdir)
            engine.pdf_conv.convert(outdir, outdir)
            cand._attach_outputs(outdir)
        return True

    def _build_docx(self, outdir):
        self.ensure_one()
        os.makedirs(outdir, exist_ok=True)
        base = engine.gen_cv.to_filename(self.name)
        docx = os.path.join(outdir, base + ".docx")
        engine.gen_cv.build(self.to_dict(), docx)
        return docx

    def _attach_outputs(self, outdir):
        self.ensure_one()
        base = engine.gen_cv.to_filename(self.name)
        docx = os.path.join(outdir, base + ".docx")
        pdf = os.path.join(outdir, base + ".pdf")
        if os.path.exists(docx):
            self.write({
                "output_docx": base64.b64encode(open(docx, "rb").read()),
                "output_docx_name": base + ".docx",
            })
        if os.path.exists(pdf):
            self.write({
                "output_pdf": base64.b64encode(open(pdf, "rb").read()),
                "output_pdf_name": base + ".pdf",
            })
        self._attach_supporting_docs()

    def _attach_supporting_docs(self):
        self.ensure_one()
        pack = self.pack_id
        Att = self.env["ir.attachment"]
        for line in (self.docs or "").splitlines():
            m = re.search(r"\(see: (.+)\)", line)
            if not m:
                continue
            fname = m.group(1).strip()
            src = engine.cv_std.resolve_doc_path(pack.engine_id, fname)
            if not src or not os.path.exists(src):
                continue
            if Att.search_count([("res_model", "=", "cv.candidate"),
                                 ("res_id", "=", self.id),
                                 ("name", "=", fname)]):
                continue
            Att.create({
                "name": fname,
                "res_model": "cv.candidate",
                "res_id": self.id,
                "datas": base64.b64encode(open(src, "rb").read()),
            })

    # ------------------------------------------------------------ downloads
    def _supporting_attachments(self):
        self.ensure_one()
        return self.env["ir.attachment"].search([
            ("res_model", "=", "cv.candidate"),
            ("res_id", "=", self.id),
            ("res_field", "=", False),
        ])

    def _download_action(self, kind):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": "/cv_studio/download/candidate/%d/%s" % (self.id, kind),
            "target": "self",
        }

    def action_download_pdf(self):
        return self._download_action("pdf")

    def action_download_docx(self):
        return self._download_action("docx")
