# -*- coding: utf-8 -*-
"""Build Zakheni-standard CV DOCX files from candidate dicts (BSDS batch).

Schema per candidate:
    name: str, full name (used for filename "<name> - Zakheni CV")
    target_role: str (e.g. "Business Analyst")
    summary: list[str] paragraphs and/or bullets (prefix with "- " for bullets)
    competencies: list[[label, text]]  -> Core Technical Competencies
    certs: list[str]
    education: list[{name, detail, dates}] or list[str]
    career: list[{company, title, dates, bullets}]
    refs: list[str]
    docs: list[str]  -> Supporting Documents section (each cert/doc listed separately)
"""
import os
import sys

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

NAVY = RGBColor(0x1F, 0x3A, 0x5F)
GREY = RGBColor(0x55, 0x55, 0x55)
LGREY = RGBColor(0xA5, 0xA7, 0xA8)

LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media", "image1.png")


def _set_font(run, size, bold=False, italic=False, color=None, font="Calibri"):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), font)
    rFonts.set(qn("w:hAnsi"), font)
    rFonts.set(qn("w:cs"), font)


def _rule(p, color="1F3A5F", size="12", space="4"):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), space)
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def _p(doc, text, size=10.5, bold=False, italic=False, color=None,
       after=6, before=0, bullets=False, hang=None, align=None):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after = Pt(after)
    pf.space_before = Pt(before)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.15
    if align == "center":
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if bullets:
        pf.left_indent = Inches(0.25)
        pf.first_line_indent = Inches(-0.15)
    elif hang:
        pf.left_indent = Inches(hang)
        pf.first_line_indent = Inches(-0.18)
    r = p.add_run(("" if not bullets else "\u2022  ") + text)
    _set_font(r, size, bold, italic, color)
    return p


def _heading(doc, text):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(8)
    pf.space_after = Pt(4)
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    pf.line_spacing = 1.15
    r = p.add_run(text.upper())
    _set_font(r, 14, bold=True, color=NAVY)
    _rule(p)
    return p


def build(c, outpath):
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Inches(8.5)
    sec.page_height = Inches(11)
    sec.top_margin = Inches(1.5)
    sec.left_margin = Inches(1.25)
    sec.right_margin = Inches(1.25)
    sec.bottom_margin = Inches(1.1)
    sec.header_distance = Inches(0.5)
    sec.footer_distance = Inches(0.7)

    hdr = sec.header
    hp = hdr.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = hp.add_run()
    run.add_picture(LOGO, width=Inches(1.43))

    ftr = sec.footer
    fp = ftr.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    _rule(fp, color="A5A7A8", size="8", space="1")
    fr = fp.add_run()
    _set_font(fr, 10.5)
    fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
    fr._r.append(fld1); fr._r.append(instr); fr._r.append(fld2)
    fr2 = fp.add_run(" | ")
    _set_font(fr2, 10.5)
    fr3 = fp.add_run("P a g e")
    _set_font(fr3, 10.5, color=RGBColor(0x7F, 0x7F, 0x7F))

    # name
    _p(doc, c["name"], size=18, bold=True, color=NAVY, after=4, before=0)
    # target role
    _p(doc, "Target Role: " + c["target_role"], size=12, bold=True, color=GREY, after=2)
    # rule under header block
    pr = doc.paragraphs[-1]
    _rule(pr)

    def render_list(items):
        for it in items:
            if isinstance(it, dict):
                line = " ".join(x for x in [it.get("name"), it.get("detail"), it.get("dates")] if x)
                _p(doc, line, bullets=True)
            else:
                _p(doc, it, bullets=True)

    # Professional Summary
    if c.get("summary"):
        _heading(doc, "Professional Summary")
        for para in c["summary"]:
            if para.startswith("- "):
                _p(doc, para[2:], bullets=True)
            else:
                _p(doc, para)

    # Core Technical Competencies
    if c.get("competencies"):
        _heading(doc, "Core Technical Competencies")
        for label, text in c["competencies"]:
            p = _p(doc, "", bullets=True)
            r1 = p.add_run(label + ": ")
            _set_font(r1, 10.5, bold=True)
            r2 = p.add_run(text)
            _set_font(r2, 10.5)

    # Certifications
    if c.get("certs"):
        _heading(doc, "Certifications")
        render_list(c["certs"])

    # Education
    if c.get("education"):
        _heading(doc, "Education")
        for it in c["education"]:
            if isinstance(it, dict):
                _p(doc, "", after=0)
                p = doc.paragraphs[-1]
                pf = p.paragraph_format
                pf.left_indent = Inches(0.4)
                r = p.add_run(it.get("institution", ""))
                _set_font(r, 10.5, bold=True)
                if it.get("qual"):
                    r2 = p.add_run(" - " + it["qual"])
                    _set_font(r2, 10.5)
                if it.get("dates"):
                    p2 = doc.add_paragraph()
                    p2.paragraph_format.left_indent = Inches(0.4)
                    p2.paragraph_format.space_after = Pt(6)
                    r3 = p2.add_run(it["dates"])
                    _set_font(r3, 9.5, italic=True, color=GREY)
            else:
                _p(doc, it, bullets=True)

    # Career History
    if c.get("career"):
        _heading(doc, "Professional Experience")
        for job in c["career"]:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(job.get("company", ""))
            _set_font(r, 11, bold=True)
            dates = job.get("dates")
            if dates:
                r2 = p.add_run("  |  " + dates)
                _set_font(r2, 10.5, italic=True, color=GREY)
            if job.get("title"):
                p2 = doc.add_paragraph()
                p2.paragraph_format.space_after = Pt(2)
                p2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
                p2.paragraph_format.line_spacing = 1.15
                r3 = p2.add_run(job["title"])
                _set_font(r3, 9.5, italic=True, color=GREY)
            for b in job.get("bullets", []):
                _p(doc, b, bullets=True, after=2)

    # References
    if c.get("refs"):
        _heading(doc, "References")
        refs = c["refs"]
        if isinstance(refs, list) and len(refs) > 1:
            _p(doc, "Available upon request.", bullets=True)
            for r_ in refs:
                _p(doc, r_, bullets=True)
        else:
            _p(doc, refs[0] if isinstance(refs, list) else refs, bullets=True)

    # Supporting Documents
    if c.get("docs"):
        _heading(doc, "Supporting Documents")
        for it in c["docs"]:
            _p(doc, it, bullets=True)

    doc.save(outpath)


def to_filename(name):
    return _sanitize(name) + " - Zakheni CV"


def _sanitize(s):
    import re
    s = re.sub(r'[\\/:*?"<>|]', "", s).strip()
    return re.sub(r"\s+", " ", s)


if __name__ == "__main__":
    import glob
    src = sys.argv[1] if len(sys.argv) > 1 else "candidates_bsds.py"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "out"
    ns = {"__name__": "not_main"}
    exec(open(src, encoding="utf-8").read(), ns)
    cands = ns["CANDIDATES"]
    os.makedirs(outdir, exist_ok=True)
    for key, c in cands.items():
        c.setdefault("docs", [])
        fn = to_filename(c["name"]) + ".docx"
        p = os.path.join(outdir, fn)
        build(c, p)
        print("built", key, "->", p)