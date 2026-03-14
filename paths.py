# ============================================================
# paths.py — Antigravity Multi-Agent System
# Adds all numbered subdirectories to sys.path so Python can
# import from them regardless of the numeric folder prefix.
# Import this FIRST in any entry-point file.
# ============================================================

import sys
import os

_BASE = os.path.dirname(os.path.abspath(__file__))

_SUBDIRS = [
    "1_config",
    "2_core",
    "3_connectors",
    "4_tools",
    "5_skills",
    "6_workflows",
    "7_interfaces",
]

for _d in _SUBDIRS:
    _p = os.path.join(_BASE, _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Also ensure root is on path (for paths.py itself to be re-importable)
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)
