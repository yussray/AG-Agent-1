# ============================================================
# file_reader.py — Antigravity Multi-Agent System
# Read various file formats (txt, pdf, docx, xlsx, csv)
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging

logger = logging.getLogger("antigravity.file_reader")


def read_file(path: str) -> str:
    """Read a file and return its text content."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext in (".txt", ".md", ".py", ".json", ".yaml", ".yml", ".csv"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    elif ext == ".pdf":
        try:
            from reportlab.pdfgen import canvas  # noqa
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except ImportError:
            return f"[PDF reading requires pdfplumber: pip install pdfplumber]\nFile: {path}"

    elif ext in (".docx",):
        try:
            from docx import Document
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            return f"[DOCX reading requires python-docx: pip install python-docx]\nFile: {path}"

    elif ext in (".xlsx", ".xls"):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(path)
            lines = []
            for ws in wb.worksheets:
                for row in ws.iter_rows(values_only=True):
                    lines.append("\t".join(str(c) for c in row if c is not None))
            return "\n".join(lines)
        except ImportError:
            return f"[Excel reading requires openpyxl: pip install openpyxl]\nFile: {path}"

    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
