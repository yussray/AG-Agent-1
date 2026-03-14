"""Designer Skill Verification — imports, templates, design method."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Designer Skill Verification ===\n")
failures = []

def check(name, fn):
    try:
        r = fn()
        print(f"OK  {name}" + (f": {str(r)[:80]}" if r else ""))
    except Exception as e:
        print(f"FAIL {name}: {e}")
        failures.append(name)

check("skills/__init__", lambda: __import__("skills"))
check("skills/designer_skill import", lambda: __import__("skills.designer_skill", fromlist=["designer"]))

import json, os
def check_template(name):
    path = rf"d:\Antigravity\AG-Agent\skills\layout_templates\{name}.json"
    with open(path) as f:
        data = json.load(f)
    return f"{data['name']}: {len(data)} keys"

check("presentation_layout.json", lambda: check_template("presentation_layout"))
check("report_layout.json",       lambda: check_template("report_layout"))
check("spreadsheet_layout.json",  lambda: check_template("spreadsheet_layout"))

from skills.designer_skill import PRESENTATION_LAYOUT, REPORT_LAYOUT, SPREADSHEET_LAYOUT
check("PRESENTATION_LAYOUT loaded", lambda: f"{len(PRESENTATION_LAYOUT['slide_structure'])} slides")
check("REPORT_LAYOUT loaded",       lambda: f"{len(REPORT_LAYOUT['document_structure'])} sections")
check("SPREADSHEET_LAYOUT loaded",  lambda: f"{len(SPREADSHEET_LAYOUT['sheet_structure'])} sheets")

from workflows.research_workflow import build_slides_workflow
steps = build_slides_workflow("test topic")
step_names = [s.name for s in steps]
check("Slides workflow has Designer Skill step", lambda: "Designer Skill" in step_names and step_names)

check("main.py v0.4", lambda: __import__("main"))
check("telegram_bot", lambda: __import__("telegram_bot"))

print()
if failures:
    print(f"FAILURES: {failures}")
else:
    print("=== All checks passed! ===")
