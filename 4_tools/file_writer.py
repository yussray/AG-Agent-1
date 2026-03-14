# ============================================================
# file_writer.py — Antigravity Multi-Agent System
# Write text content to files
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from config import OUTPUT_DIR

logger = logging.getLogger("antigravity.file_writer")


def write_file(content: str, filename: str, directory: str = None) -> str:
    """
    Write text content to a file.

    Args:
        content: Text to write
        filename: Filename (e.g. "report.txt")
        directory: Directory path (defaults to OUTPUT_DIR)

    Returns:
        Absolute path of the written file
    """
    dir_path = directory or OUTPUT_DIR
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Written: {path}")
    return os.path.abspath(path)


def append_file(content: str, filename: str, directory: str = None) -> str:
    """Append text to an existing file (or create it)."""
    dir_path = directory or OUTPUT_DIR
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, filename)

    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"Appended: {path}")
    return os.path.abspath(path)
