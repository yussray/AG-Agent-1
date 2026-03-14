# ============================================================
# ocr_reader.py — Antigravity Multi-Agent System
# Extract text from images using Vision connector
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from vision_connector import vision

logger = logging.getLogger("antigravity.ocr")


def extract_text_from_image(image_source: str) -> str:
    """
    Extract text from an image (OCR) using MedGemma vision model.

    Args:
        image_source: File path, URL, or base64 string

    Returns:
        Extracted text from the image
    """
    if not vision.is_available():
        return (
            f"Vision model not loaded. Run: ollama pull {vision.model}\n"
            "Make sure Ollama is running."
        )

    return vision.extract_text(image_source)
