# ============================================================
# image_analysis.py — Antigravity Multi-Agent System
# General image analysis using Vision connector
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from vision_connector import vision

logger = logging.getLogger("antigravity.image_analysis")


def analyze_image(image_source: str, task: str = "describe", clinical_context: str = "") -> str:
    """
    Analyze an image using the Vision connector.

    Args:
        image_source: File path, URL, or base64 string
        task: 'describe' | 'medical_analysis' | 'ocr' | 'screenshot'
        clinical_context: Optional context for medical analysis

    Returns:
        Analysis text from the vision model
    """
    if not vision.is_available():
        return (
            f"Vision model not loaded. Run: ollama pull {vision.model}\n"
            "Make sure Ollama is running before requesting image analysis."
        )

    params = {}
    if clinical_context:
        params["clinical_context"] = clinical_context

    return vision.dispatch(task, image_source, params)


def describe_image(image_source: str) -> str:
    """Describe an image in detail."""
    return analyze_image(image_source, task="describe")


def analyze_medical_image(image_source: str, context: str = "") -> str:
    """Perform medical image analysis."""
    return analyze_image(image_source, task="medical_analysis", clinical_context=context)
