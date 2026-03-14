# ============================================================
# export_csv.py — Antigravity Multi-Agent System
# Export data to CSV files
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import csv
import logging
from config import OUTPUT_DIR

logger = logging.getLogger("antigravity.export_csv")


def export_csv(
    headers: list,
    rows: list,
    filename: str = "export.csv",
    directory: str = None
) -> str:
    """
    Export data to a CSV file.

    Args:
        headers: List of column names
        rows: List of row value lists
        filename: Output filename
        directory: Output directory (defaults to OUTPUT_DIR)

    Returns:
        Absolute path of the written CSV file
    """
    dir_path = directory or OUTPUT_DIR
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, filename)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

    logger.info(f"CSV exported: {path} ({len(rows)} rows)")
    return os.path.abspath(path)
