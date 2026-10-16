# -*- coding: utf-8 -*-
"""Thin wrapper around the bundled CV standardiser engine.

The engine modules (cv_std, gen_cv, ...) use flat imports, so this module puts
the bundle on ``sys.path`` and imports them by name. It also maps Odoo config
parameters onto the engine's runtime roots.
"""
import os
import sys

_ENGINE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "engine")
if _ENGINE_DIR not in sys.path:
    sys.path.insert(0, _ENGINE_DIR)

import cv_std      # noqa: E402
import gen_cv      # noqa: E402
import pdf_conv    # noqa: E402
import autodraft   # noqa: E402
import llm_draft   # noqa: E402

__all__ = ["cv_std", "gen_cv", "pdf_conv", "autodraft", "llm_draft",
           "configure", "DEFAULTS"]

DEFAULT_OPENCODE_EXE = r"C:\Users\jerma\Downloads\Dev and Code\opencode-windows-x64\opencode.exe"
DEFAULT_MODEL = "opencode/big-pickle"
DEFAULTS = {
    "cv_studio.work_root": "",
    "cv_studio.dest_root": cv_std.DEST_ROOT,
    "cv_studio.opencode_exe": DEFAULT_OPENCODE_EXE,
    "cv_studio.model": DEFAULT_MODEL,
    "cv_studio.max_chars": "20000",
    "cv_studio.timeout": "300",
}


def configure(work_root=None, dest_root=None, opencode_exe=None, model=None):
    """Apply runtime configuration to the engine (call before any operation)."""
    cv_std.set_roots(work_root=work_root or None, dest_root=dest_root or None)
    if opencode_exe:
        llm_draft.OPENCODE_EXE = opencode_exe
    if model:
        llm_draft.MODEL = model
