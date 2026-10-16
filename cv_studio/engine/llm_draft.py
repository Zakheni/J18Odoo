# -*- coding: utf-8 -*-
"""LLM-backed drafting: asks opencode.exe to turn a CV's text into the Zakheni
schema. This reproduces house quality (curation + summarising), unlike the
heuristic autodraft module.
"""
import json
import os
import re
import subprocess

from autodraft import clean_name, describe_doc

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

OPENCODE_EXE = os.environ.get(
    "OPENCODE_EXE",
    r"C:\Users\jerma\Downloads\Dev and Code\opencode-windows-x64\opencode.exe")
MODEL = os.environ.get("CV_LLM_MODEL", "opencode/big-pickle")

# Minimal headless config: skip MCP servers (Playwright/tasker) and AGENTS
# instructions. This cuts each drafting call from ~30-70s to ~10s and stops the
# agent from doing anything but reading the CV and answering.
MINIMAL_CONFIG = os.environ.get(
    "CV_LLM_CONFIG", '{"mcp":{},"instructions":[],"permission":"allow"}')

PROMPT = """Read the file: {txt}

Using ONLY information present in that CV text (never invent anything), output a single JSON object
between the markers <<<JSON>>> and <<<END>>> and nothing else. Do not write any files. JSON keys:
{{"name": str, "target_role": str, "summary": [str],
"competencies": [[label, text]], "certs": [str],
"education": [{{"institution": str, "qual": str, "dates": str}}],
"career": [{{"company": str, "title": str, "dates": str, "bullets": [str]}}],
"refs": [str]}}
Rules:
- name = the candidate's full name ({name_hint}).
- target_role = "{role}".
- summary = a 3-5 sentence professional profile, as a list of 1-3 strings; a string starting with "- " renders as a bullet.
- competencies = 5-10 real [short label, one-line description] pairs.
- certs = real certifications/qualifications only, max 12, each with issuer/year if present.
- education = real institutions + qualification + years.
- career = real jobs newest first, max 6, each with company, title, dates and 4-5 concise bullets.
- refs = real referees if listed, else ["Available on request."].
Output ONLY the JSON between the markers."""


def _clean(s):
    return ANSI.sub("", s or "")


def _extract_json(out):
    m = re.search(r"<<<JSON>>>(.*?)<<<END>>>", out, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        i, j = out.find("{"), out.rfind("}")
        raw = out[i:j + 1] if i != -1 and j > i else ""
    raw = raw.strip().strip("`").strip()
    raw = re.sub(r"^json\s*", "", raw, flags=re.I)
    return json.loads(raw)


def draft_via_llm(txt_path, name="", role="", docs=None, model=None, exe=None,
                  timeout=300, max_chars=20000):
    exe = exe or OPENCODE_EXE
    model = model or MODEL
    if not os.path.exists(exe):
        raise FileNotFoundError(f"opencode.exe not found: {exe}")
    src = os.path.abspath(txt_path)
    with open(src, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    if len(text) > max_chars:
        head = int(max_chars * 0.6)
        tail = max_chars - head
        text = (text[:head] + "\n...[middle omitted]...\n" + text[-tail:])
        trimmed = os.path.join(os.path.dirname(src),
                               "_trimmed_" + os.path.basename(src))
        with open(trimmed, "w", encoding="utf-8") as fh:
            fh.write(text)
        src = trimmed
    prompt = PROMPT.format(txt=src, name_hint=name, role=role)
    env = dict(os.environ)
    env["OPENCODE_CONFIG_CONTENT"] = MINIMAL_CONFIG
    env.setdefault("PYTHONIOENCODING", "utf-8")
    proc = subprocess.run([exe, "run", "-m", model, prompt],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout, env=env,
                          cwd=os.path.dirname(src))
    out = _clean((proc.stdout or "") + "\n" + (proc.stderr or ""))
    data = _extract_json(out)
    cand = {
        "name": clean_name(data.get("name") or name),
        "role": role or "",
        "target_role": data.get("target_role") or role or "",
        "summary": data.get("summary") or [""],
        "competencies": data.get("competencies") or [],
        "certs": data.get("certs") or [],
        "education": data.get("education") or [],
        "career": data.get("career") or [],
        "refs": data.get("refs") or ["Available on request."],
        "docs": [f"{describe_doc(d['base'])} (see: {d['base']})"
                 for d in (docs or [])],
    }
    if isinstance(cand["summary"], str):
        cand["summary"] = [cand["summary"]]
    return cand
