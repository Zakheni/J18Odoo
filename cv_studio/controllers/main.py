# -*- coding: utf-8 -*-
import base64
import io
import os
import uuid
import zipfile

from odoo import http
from odoo.http import request
from odoo.addons.cv_studio.services import engine


class CvStudioDownload(http.Controller):

    @http.route("/cv_studio/upload_pack", type="http", auth="user",
                methods=["POST"], csrf=False, max_content_length=None)
    def upload_pack(self, **kw):
        """Receive a pack zip as a streamed multipart upload.

        The browser sends the file as-is (no base64), so the request is ~25%
        smaller than a JSON-RPC form save and is written straight to disk.
        ``max_content_length=None`` lifts Odoo's own body cap on this route.
        """
        ufile = request.httprequest.files.get("ufile")
        if not ufile or not ufile.filename:
            return request.make_json_response(
                {"error": "No file was received."}, status=400)
        pack_model = request.env["cv.pack"]
        pack_model._apply_engine_config()
        updir = pack_model._uploads_dir()
        os.makedirs(updir, exist_ok=True)
        token = uuid.uuid4().hex
        ext = os.path.splitext(ufile.filename)[1].lower() or ".zip"
        if ext not in (".zip", ".tar", ".gz"):
            ext = ".zip"
        path = os.path.join(updir, token + ext)
        with open(path, "wb") as fh:
            ufile.save(fh)
        return request.make_json_response({
            "token": token,
            "name": ufile.filename,
            "size": os.path.getsize(path),
        })

    def _stream(self, data, filename, mimetype):
        return request.make_response(
            data,
            headers=[
                ("Content-Type", mimetype),
                ("Content-Disposition", 'attachment; filename="%s"' % filename),
                ("Content-Length", str(len(data))),
            ],
        )

    @http.route("/cv_studio/download/candidate/<int:candidate_id>/<string:kind>",
                type="http", auth="user")
    def download_candidate(self, candidate_id, kind, **kw):
        cand = request.env["cv.candidate"].browse(candidate_id).exists()
        if not cand:
            return request.not_found()
        if kind == "pdf":
            data = cand.output_pdf
            name = cand.output_pdf_name or (cand.name + ".pdf")
            mime = "application/pdf"
        elif kind == "docx":
            data = cand.output_docx
            name = cand.output_docx_name or (cand.name + ".docx")
            mime = ("application/vnd.openxmlformats-officedocument"
                    ".wordprocessingml.document")
        else:
            return request.not_found()
        if not data:
            return request.not_found()
        return self._stream(base64.b64decode(data), name, mime)

    @http.route("/cv_studio/download/pack/<int:pack_id>/zip",
                type="http", auth="user")
    def download_pack(self, pack_id, **kw):
        pack = request.env["cv.pack"].browse(pack_id).exists()
        if not pack:
            return request.not_found()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for cand in pack.candidate_ids:
                folder = (cand.name or ("candidate_%s" % cand.id)) + "/"
                if cand.output_docx:
                    z.writestr(folder + (cand.output_docx_name
                                         or cand.name + ".docx"),
                               base64.b64decode(cand.output_docx))
                if cand.output_pdf:
                    z.writestr(folder + (cand.output_pdf_name
                                         or cand.name + ".pdf"),
                               base64.b64decode(cand.output_pdf))
                for att in cand._supporting_attachments():
                    if att.datas:
                        z.writestr(folder + att.name, base64.b64decode(att.datas))
        data = buf.getvalue()
        name = (pack.name or "cv_pack").replace("/", "_") + ".zip"
        return self._stream(data, name, "application/zip")
