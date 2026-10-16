# -*- coding: utf-8 -*-
"""Convert DOCX -> PDF via Word COM with kill-and-retry resilience."""
import os
import sys
import time
import subprocess
import glob

import win32com.client as win32

try:
    import pythoncom
except Exception:  # noqa: BLE001
    pythoncom = None


def _ensure_com():
    """Word COM automation needs the calling thread to initialise COM; Odoo
    request/worker threads do not do this for us."""
    if pythoncom is not None:
        try:
            pythoncom.CoInitialize()
        except Exception:  # noqa: BLE001
            pass


def kill_word():
    try:
        subprocess.run(["taskkill", "/F", "/IM", "WINWORD.EXE"],
                       capture_output=True, text=True)
    except Exception:
        pass
    time.sleep(2)


def convert(pdf_dir, docx_dir):
    _ensure_com()
    os.makedirs(pdf_dir, exist_ok=True)
    docx = sorted(glob.glob(os.path.join(docx_dir, "*.docx")))
    todo = []
    for d in docx:
        base = os.path.splitext(os.path.basename(d))[0] + ".pdf"
        pd = os.path.join(pdf_dir, base)
        if not os.path.exists(pd):
            todo.append((d, pd))
    if not todo:
        print("all converted")
        return
    for attempt in range(3):
        try:
            kill_word()
            word = win32.DispatchEx("Word.Application")
            word.Visible = False
        except Exception as e:
            print("word init fail:", e)
            continue
        ok = True
        try:
            for i, (d, pd) in enumerate(todo):
                try:
                    doc = word.Documents.Open(d, ReadOnly=True)
                    doc.SaveAs2(pd, FileFormat=17)
                    doc.Close(False)
                    print("pdf", os.path.basename(pd))
                except Exception as e:
                    ok = False
                    print("FAILED", d, e)
        finally:
            try:
                word.Quit()
            except Exception:
                pass
            kill_word()
        if ok:
            break
        time.sleep(3)
    bad = [pd for _, pd in todo if not os.path.exists(pd)]
    print("remaining missing:", len(bad))


if __name__ == "__main__":
    convert(sys.argv[1] if len(sys.argv) > 1 else "pdf",
            sys.argv[2] if len(sys.argv) > 2 else "out")