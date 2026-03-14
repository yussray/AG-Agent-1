# ============================================================
# folder_manager.py — Antigravity Multi-Agent System
# Manage output directories and file organization
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import shutil
import logging
from config import OUTPUT_DIR

logger = logging.getLogger("antigravity.folder_manager")


def ensure_dir(path: str) -> str:
    """Create directory if it doesn't exist. Returns path."""
    os.makedirs(path, exist_ok=True)
    return path


def list_outputs(directory: str = None) -> list[dict]:
    """List all files in the output directory."""
    dir_path = directory or OUTPUT_DIR
    if not os.path.exists(dir_path):
        return []

    files = []
    for fname in sorted(os.listdir(dir_path)):
        fpath = os.path.join(dir_path, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            files.append({
                "name": fname,
                "path": os.path.abspath(fpath),
                "size_kb": round(stat.st_size / 1024, 1),
                "ext": os.path.splitext(fname)[1].lower()
            })
    return files


def move_file(src: str, dest_dir: str) -> str:
    """Move a file to a different directory."""
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, os.path.basename(src))
    shutil.move(src, dest)
    logger.info(f"Moved: {src} -> {dest}")
    return dest


def delete_file(path: str) -> bool:
    """Delete a file. Returns True if successful."""
    try:
        os.remove(path)
        logger.info(f"Deleted: {path}")
        return True
    except Exception as e:
        logger.error(f"Could not delete {path}: {e}")
        return False


def clean_outputs(directory: str = None, keep_ext: list = None) -> int:
    """Remove files from outputs directory. Returns count of deleted files."""
    dir_path = directory or OUTPUT_DIR
    count = 0
    for f in list_outputs(dir_path):
        if keep_ext and f["ext"] in keep_ext:
            continue
        if delete_file(f["path"]):
            count += 1
    return count
