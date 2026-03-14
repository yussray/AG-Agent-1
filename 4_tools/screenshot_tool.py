# ============================================================
# screenshot_tool.py — Antigravity Multi-Agent System
# Capture and analyze screenshots
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from config import OUTPUT_DIR
from vision_connector import vision

logger = logging.getLogger("antigravity.screenshot")


def take_screenshot(filename: str = None) -> str:
    """
    Capture a screenshot of the current screen.

    Returns:
        Absolute path to saved screenshot file
    """
    try:
        import pyautogui
        from PIL import Image

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        if not filename:
            import time
            filename = f"screenshot_{int(time.time())}.png"

        path = os.path.join(OUTPUT_DIR, filename)
        screenshot = pyautogui.screenshot()
        screenshot.save(path)
        logger.info(f"Screenshot saved: {path}")
        return os.path.abspath(path)

    except ImportError:
        raise RuntimeError("pyautogui and Pillow required: pip install pyautogui Pillow")


def analyze_screenshot(image_path: str = None) -> str:
    """
    Capture a screenshot (or use existing) and analyze it.

    Args:
        image_path: Path to existing screenshot (None = take new one)

    Returns:
        Analysis text from vision model
    """
    if not image_path:
        image_path = take_screenshot()

    if not vision.is_available():
        return f"Vision model not loaded. Screenshot saved at: {image_path}"

    return vision.analyze_screenshot(image_path)
