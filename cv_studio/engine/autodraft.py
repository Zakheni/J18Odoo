# -*- coding: utf-8 -*-
"""Best-effort auto-draft of a Zakheni-format candidate from a source CV's text.

Heuristic, no fabrication: it only reorganises text already present in the
candidate's own CV. Quality varies with the source; the user reviews in the UI.
"""
import re

HONORIFIC = re.compile(r"(?i)^(mr|mrs|ms|miss|dr|prof|adv|sr|jr|sir|madam)\.?\s+")

PAGE_NOISE = [
    re.compile(r"(?i)^page\s*\d+(\s*(of|/)\s*\d+)?$"),
    re.compile(r"^[\-\._•·\s]+$"),
    re.compile(r"(?i)^(curriculum\s+vitae|resume|cv)$"),
]

HEADINGS = {
    "summary": ["professional summary", "executive summary", "career summary", "personal profile",
                "profile summary", "professional profile", "profile", "summary", "career objective",
                "objective", "career overview", "about me", "personal statement", "brief profile"],
    "competencies": ["core technical competencies", "core competencies", "technical competencies",
                     "key competencies", "core skills", "key skills", "technical skills",
                     "professional skills", "areas of expertise", "key areas of expertise",
                     "core areas of expertise", "competencies", "skills", "expertise",
                     "it skills", "computer skills", "technical expertise"],
    "certs": ["professional certifications", "certifications", "certification", "certificates",
              "accreditations", "training and certifications", "courses and certifications",
              "other short courses", "short courses", "course history", "courses",
              "professional development", "training", "certificates and training"],
    "education": ["educational background", "education and training", "academic qualifications",
                  "academic background", "academic history", "educational qualifications",
                  "qualifications", "education", "education & training"],
    "career": ["professional experience", "work experience", "employment history", "work history",
               "career history", "career summary", "professional background", "relevant experience",
               "key experience", "experience", "employment", "career"],
    "refs": ["references", "referees", "reference"],
    "personal": ["personal details", "personal information", "personal particulars"],
}

CONTACT_RE = re.compile(r"(?i)(@|\b(tel|cell|mobile|phone|contact|email|e-mail|address|"
                        r"id number|identity)\b|\+?\d[\d\s\-()]{6,})")
DATE_RE = re.compile(r"(?i)\b((jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s*\d{4}"
                     r"|\d{1,2}/\d{4}|\d{4})\b")
YEAR_RE = re.compile(r"(19|20)\d{2}")
INSTITUTION_RE = re.compile(r"(?i)(university|univ\b|college|school|institute|technikon|academy|"
                            r"polytechnic|unisa\b|tut\b|wits|stellenbosch|ukzn|up\b|uj\b|nwu|"
                            r"business\s+school|varsity)")

DEGREE_RE = re.compile(r"(?i)(bsc|b\.sc|btech|b\.tech|bcom|b\.com|\bba\b|mba|\bmsc\b|m\.sc|"
                       r"\bma\b|phd|master|bachelor|honours|honors|diploma|degree|"
                       r"national diploma|higher certificate|senior certificate|\bmatric\b|"
                       r"\bnsc\b|national senior|certificate)")

STOP = {"institution", "qualification", "year", "course", "course:", "period", "company",
        "company name", "position", "position held", "job title", "title", "role", "designation",
        "rank", "duration", "date", "dates", "name", "address", "contact", "contact no",
        "email", "e-mail", "client", "project name", "resource role", "dates involved",
        "responsibilities", "responsibilities held", "key projects", "achievements",
        "personal details", "personal information", "references", "referees", "frequency",
        "from", "to", "present", "description", "institution name"}

LAB_JOIN = re.compile(r"(?i)^(company\s*name|company|employer|organisation|organization|"
                      r"position held|position|job title|title|role|designation|rank|period|"
                      r"duration|dates|date|tenure|from|name|address|contact(\s*no)?|"
                      r"email|e-mail|telephone|tel|cell|mobile)\s*:?$")


def _norm(s):
    return s.strip().strip(":").strip().lower()


def is_stop(line):
    return _norm(line) in STOP or len(line.strip(" :.-_")) < 2


NAME_PARTICLES = {"van", "von", "der", "de", "del", "della", "den", "du", "da",
                  "dos", "le", "la", "ter", "ten", "op", "bin", "al", "el", "st"}


def _cap_word(w):
    low = w.lower()
    if "'" in low:
        a, _, b = low.partition("'")
        return f"{a.capitalize()}'{b.capitalize()}"
    if low.startswith("mc") and len(low) > 2:
        return "Mc" + low[2:].capitalize()
    if low.startswith("mac") and len(low) > 3:
        return "Mac" + low[3:].capitalize()
    return low.capitalize()


def _title_name(n):
    out = []
    wi = 0
    for tok in re.split(r"(\s+|-)", n):
        if not tok or tok.isspace() or tok == "-":
            out.append(tok)
            continue
        if wi > 0 and tok.lower() in NAME_PARTICLES:
            out.append(tok.lower())
        else:
            out.append(_cap_word(tok))
        wi += 1
    return "".join(out)


def clean_name(n):
    n = re.sub(r"\s+", " ", (n or "")).strip(" .,-_")
    n = HONORIFIC.sub("", n, count=1).strip()
    letters = [c for c in n if c.isalpha()]
    if letters and all(c.isupper() for c in letters):
        n = _title_name(n)
    return n.strip()


def clean_lines(text):
    out = []
    for ln in (text or "").replace("\u2022", "•").split("\n"):
        t = re.sub(r"[ \t\u00a0]+", " ", ln).replace("\ufffd", "-").strip()
        if not t:
            continue
        if any(p.match(t) for p in PAGE_NOISE):
            continue
        out.append(t)
    out = merge_labels(out)
    return out


def merge_labels(lines):
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if LAB_JOIN.match(ln) and i + 1 < len(lines) and lines[i + 1].lstrip().startswith(":"):
            out.append(re.sub(r":?\s*$", "", ln).strip() + " " + lines[i + 1].strip())
            i += 2
            continue
        out.append(ln)
        i += 1
    return out


def canon_heading(line):
    s = line.strip().strip(":").strip()
    s = re.sub(r"[^a-z& ]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    if not s or len(s) > 46:
        return None
    for sec, keys in HEADINGS.items():
        if s in keys:
            return sec
    for sec, keys in HEADINGS.items():
        if any(s.startswith(k + " ") or s == k for k in keys):
            return sec
    return None


def split_sections(lines):
    secs = {"preamble": []}
    cur = "preamble"
    for ln in lines:
        sec = canon_heading(ln)
        if sec:
            cur = sec
            secs.setdefault(cur, [])
            continue
        secs.setdefault(cur, []).append(ln)
    return secs


def _strip_bullet(s):
    return s.lstrip("•-*–—\t ").strip()


def parse_summary(secs, name):
    src = secs.get("summary") or secs.get("preamble") or []
    parts = []
    for ln in src:
        if CONTACT_RE.search(ln) and len(ln) < 80:
            continue
        if clean_name(ln).lower() == name.lower():
            continue
        parts.append(_strip_bullet(ln))
    txt = re.sub(r"\s+", " ", " ".join(parts)).strip()
    if len(txt) > 1200:
        txt = txt[:1200].rsplit(" ", 1)[0] + "."
    return [txt] if txt else [""]


def _items(lines):
    return [x for x in (_strip_bullet(l) for l in lines) if x and not is_stop(x)]


def parse_competencies(secs):
    items = _items(secs.get("competencies", []))
    pairs = []
    unlabelled = []
    for it in items:
        m = re.match(r"^([A-Za-z][A-Za-z /&+.]{1,40}?)\s*[:\-]\s+(.+)$", it)
        if m and len(m.group(1)) <= 34:
            pairs.append([m.group(1).strip(), m.group(2).strip()])
        else:
            unlabelled.append(it)
    if not pairs and unlabelled:
        pairs = [["Core Technical Competencies", "; ".join(unlabelled)]]
    elif unlabelled:
        pairs.append(["Additional", "; ".join(unlabelled)])
    return pairs


def parse_certs(secs):
    return _items(secs.get("certs", []))


def parse_education(secs):
    raw = _items(secs.get("education", []))
    items = [it for it in raw
             if DEGREE_RE.search(it) or INSTITUTION_RE.search(it) or YEAR_RE.search(it)]
    out = []
    for it in items:
        years = YEAR_RE.findall(it)
        yr = re.findall(r"(?:19|20)\d{2}", it)
        dates = " - ".join(dict.fromkeys(yr)) if yr else ""
        qual = it
        inst = ""
        if INSTITUTION_RE.search(it) and len(it.split()) > 2:
            m = re.split(r"\s{2,}|,|\|| - ", it, maxsplit=1)
            if m and INSTITUTION_RE.search(m[0]):
                inst = m[0].strip()
                qual = m[1].strip() if len(m) > 1 else it
        if yr:
            qual = re.sub(r"(?i)\b((19|20)\d{2}( to (19|20)\d{2})?)\b", "", qual).strip(" ,-")
        out.append({"institution": inst, "qual": qual.strip(), "dates": dates})
    return [e for e in out if e["qual"] or e["institution"]]


_COMPANY = re.compile(r"(?i)^(company\s*name|company|employer|organisation|organization)\s*[:\-]\s*(.*)$")
_TITLE = re.compile(r"(?i)^(position held|position|job title|title|role|designation|rank|"
                    r"job position)\s*[:\-]\s*(.*)$")
_PERIOD = re.compile(r"(?i)^(period|duration|dates?|tenure|from|date)\s*[:\-]\s*(.*)$")


def parse_career(secs):
    entries = []
    cur = None

    def new():
        return {"company": "", "title": "", "dates": "", "bullets": []}

    def flush():
        if cur and (cur["company"] or cur["title"] or cur["bullets"]):
            entries.append(cur)

    for ln in secs.get("career", []):
        mc = _COMPANY.match(ln)
        mt = _TITLE.match(ln)
        mp = _PERIOD.match(ln)
        if mc:
            if cur and (cur["company"] or cur["title"] or cur["bullets"]):
                flush()
            cur = new()
            cur["company"] = mc.group(2).strip()
            continue
        if cur is None:
            cur = new()
        if mt and not cur["title"]:
            cur["title"] = mt.group(2).strip()
            continue
        if mp and not cur["dates"]:
            cur["dates"] = mp.group(2).strip()
            continue
        b = _strip_bullet(ln)
        if b:
            cur["bullets"].append(b)
    flush()
    for e in entries:
        if not e["dates"]:
            m = re.search(r"(?i)((?:[a-z]+\.?\s*)?\d{4}\s*(?:-|–|to|until)\s*"
                          r"(?:[a-z]+\.?\s*)?(?:\d{4}|present|current|date))", e["company"] + " " + e["title"])
            if m:
                e["dates"] = m.group(1).strip()
    return entries


def parse_refs(secs):
    items = _items(secs.get("refs", []))
    return items or ["Available on request."]


def describe_doc(base):
    stem = re.sub(r"\.(pdf|docx?|jpe?g|png|gif|bmp|tiff?|txt)$", "", base, flags=re.I)
    stem = re.sub(r"[_]+", " ", stem).strip()
    low = base.lower()
    if re.search(r"(id\b|identity|\.id|_id|passport)", low):
        return "Identity document"
    if re.search(r"(matric|senior certificate|nsc)", low):
        return "Matric certificate"
    if re.search(r"(cert|certificate|diploma|degree|baccalaure|qualif|transcript|award|"
                 r"complete|completion|achievement)", low):
        return "Certification/qualification"
    if re.search(r"(resume|cv\b|curriculum)", low):
        return "Curriculum vitae"
    return "Supporting document"


def draft_from_text(text, name="", role="", docs=None):
    name = clean_name(name)
    lines = clean_lines(text)
    secs = split_sections(lines)
    cand = {
        "name": name,
        "role": role or "",
        "target_role": role or "",
        "summary": parse_summary(secs, name),
        "competencies": parse_competencies(secs),
        "certs": parse_certs(secs),
        "education": parse_education(secs),
        "career": parse_career(secs),
        "refs": parse_refs(secs),
        "docs": [],
    }
    for d in (docs or []):
        base = d["base"] if isinstance(d, dict) else str(d)
        cand["docs"].append(f"{describe_doc(base)} (see: {base})")
    return cand
