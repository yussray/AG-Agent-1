# ============================================================
# medical_image_reader.py — Antigravity Multi-Agent System
# Medical image analysis wrapper
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from vision_connector import vision

logger = logging.getLogger("antigravity.medical_image")


def analyze_medical_image(image_source: str, clinical_context: str = "") -> str:
    """
    Perform medical image analysis using MedGemma.

    Args:
        image_source: File path, URL, or base64
        clinical_context: Optional clinical history or context

    Returns:
        Structured medical report string
    """
    if not vision.is_available():
        return (
            f"Vision/medical model not loaded.\n"
            f"Run: ollama pull {vision.model}"
        )

    return vision.medical_analysis(image_source, clinical_context)
