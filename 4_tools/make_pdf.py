# ============================================================
# make_pdf.py — Antigravity Multi-Agent System
# Generate PDF reports using ReportLab
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
import re
from config import OUTPUT_DIR


def make_pdf(content: str, title: str = "Report", filename: str = None) -> str:
    """
    Generate a PDF from markdown-like text.

    Args:
        content: The report text (## headings, - bullets supported)
        title: Document title
        filename: Output filename (auto-generated if None)

    Returns:
        Absolute path to saved .pdf file
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if not filename:
        slug = re.sub(r'[^\w]', '_', title.lower())[:25]
        filename = f"report_{slug}.pdf"

    path = os.path.join(OUTPUT_DIR, filename)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Title"],
        fontSize=22, textColor=colors.HexColor("#1A1A2E"),
        spaceAfter=20
    )
    heading_style = ParagraphStyle(
        "CustomHeading", parent=styles["Heading2"],
        fontSize=14, textColor=colors.HexColor("#E94F37"),
        spaceAfter=8, spaceBefore=14
    )
    body_style = ParagraphStyle(
        "CustomBody", parent=styles["Normal"],
        fontSize=11, leading=16, spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        "CustomBullet", parent=styles["Normal"],
        fontSize=11, leading=16, leftIndent=20, spaceAfter=4
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 0.3*cm))

    for line in content.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.2*cm))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], heading_style))
        elif line.startswith("# "):
            story.append(Paragraph(line[2:], heading_style))
        elif line.startswith("- "):
            story.append(Paragraph(f"\u2022 {line[2:]}", bullet_style))
        else:
            story.append(Paragraph(line.replace("&", "&amp;"), body_style))

    doc.build(story)
    return os.path.abspath(path)
