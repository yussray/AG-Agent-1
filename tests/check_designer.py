import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")
from skills.designer_skill import designer, PRESENTATION_LAYOUT, REPORT_LAYOUT, SPREADSHEET_LAYOUT
print("OK  PRESENTATION_LAYOUT slides:", len(PRESENTATION_LAYOUT["slide_structure"]))
print("OK  REPORT_LAYOUT sections:", len(REPORT_LAYOUT["document_structure"]))
print("OK  SPREADSHEET_LAYOUT sheets:", len(SPREADSHEET_LAYOUT["sheet_structure"]))
from workflows.research_workflow import build_slides_workflow
steps = build_slides_workflow("bariatric surgery")
step_names = [s.name for s in steps]
print("OK  Slides workflow steps:", step_names)
print("OK  Designer Skill in pipeline:", "Designer Skill" in step_names)
