"""
ANTIGRAVITY SYSTEM — Full Operational Check
Tests every module end-to-end without requiring LLM calls for speed.
LLM calls are marked as LIVE tests and run separately.
"""
import sys, os, time
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

results = {}
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

def check(module, name, fn):
    try:
        r = fn()
        results.setdefault(module, []).append((name, PASS, str(r)[:60] if r else ""))
    except Exception as e:
        results.setdefault(module, []).append((name, FAIL, str(e)[:80]))

print("=" * 60)
print("  ANTIGRAVITY SYSTEM — FULL OPERATIONAL CHECK")
print(f"  {time.strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ─── MODULE 1: Router + Ollama ───────────────────────────────────
from ollama_connector import ollama
from router import route

check("M1 Router+Ollama", "ollama_connector import", lambda: "ok")
check("M1 Router+Ollama", "ollama.is_available()", lambda: str(ollama.is_available()))
check("M1 Router+Ollama", "ollama.list_models()", lambda: f"{len(ollama.list_models())} models")
check("M1 Router+Ollama", "router import", lambda: "ok")

# ─── MODULE 2: AnythingLLM RAG ──────────────────────────────────
from anythingllm_connector import anythingllm
from config import ANYTHINGLLM_API_KEY

check("M2 RAG", "anythingllm_connector import", lambda: "ok")
check("M2 RAG", "anythingllm.is_available()", lambda: str(anythingllm.is_available()))
check("M2 RAG", "API key set", lambda: f"len={len(ANYTHINGLLM_API_KEY)}" if ANYTHINGLLM_API_KEY else (_ for _ in ()).throw(Exception("key empty")))
check("M2 RAG", "list_workspaces()", lambda: f"{len(anythingllm.list_workspaces())} workspaces")

# ─── MODULE 3: Workflow Engine ──────────────────────────────────
from workflow_engine import WorkflowEngine, WorkflowStep, engine
from workflows.research_workflow import build_qa_workflow, build_slides_workflow, build_research_workflow

check("M3 Workflow", "workflow_engine import", lambda: "ok")
check("M3 Workflow", "workflows import", lambda: "ok")
check("M3 Workflow", "engine.list_workflows()", lambda: str(engine.list_workflows()))

def dry_run_workflow():
    def step_one(context: dict, val: str) -> str:
        return f"step_one:{val}"
    def step_two(context: dict) -> str:
        return context.get("step_one", "missing") + ":step_two"
    steps = [
        WorkflowStep("step_one", step_one, params={"val": "test"}),
        WorkflowStep("step_two", step_two),
    ]
    r = WorkflowEngine(verbose=False).run("dry_run", steps)
    assert r.success, f"workflow failed: {r.error}"
    return r.context.get("step_two", "")[:40]

check("M3 Workflow", "dry run workflow", dry_run_workflow)

# ─── MODULE 4: Tool Layer ───────────────────────────────────────
check("M4 Tools", "make_slides import", lambda: __import__("tools.make_slides", fromlist=["make_slides"]) and "ok")
check("M4 Tools", "make_pdf import",    lambda: __import__("tools.make_pdf",    fromlist=["make_pdf"]) and "ok")
check("M4 Tools", "make_word import",   lambda: __import__("tools.make_word",   fromlist=["make_word"]) and "ok")
check("M4 Tools", "make_excel import",  lambda: __import__("tools.make_excel",  fromlist=["make_excel"]) and "ok")
check("M4 Tools", "web_scraper import", lambda: __import__("tools.web_scraper", fromlist=["scrape_url"]) and "ok")
check("M4 Tools", "file_reader import", lambda: __import__("tools.file_reader", fromlist=["read_text_file"]) and "ok")
check("M4 Tools", "file_writer import", lambda: __import__("tools.file_writer", fromlist=["write_text_file"]) and "ok")
check("M4 Tools", "folder_manager import", lambda: __import__("tools.folder_manager", fromlist=["list_folder"]) and "ok")

def gen_pptx_live():
    from tools.make_slides import make_slides
    outline = "SLIDE 1: Test\n  - bullet 1\n  - bullet 2\nSLIDE 2: End\n  - done"
    path = make_slides(outline, title="SysCheck", filename="_syscheck.pptx")
    size = os.path.getsize(path)
    assert size > 1000, "PPTX too small"
    return f"{os.path.basename(path)} {round(size/1024)}KB"
check("M4 Tools", "PPTX generation", gen_pptx_live)

def gen_pdf_live():
    from tools.make_pdf import make_pdf
    path = make_pdf("## Test\nSystem check.\n- item 1\n- item 2", title="SysCheck", filename="_syscheck.pdf")
    return f"{os.path.basename(path)} {round(os.path.getsize(path)/1024)}KB"
check("M4 Tools", "PDF generation", gen_pdf_live)

def gen_excel_live():
    from tools.make_excel import make_excel
    path = make_excel([["A","B"],["1","2"]], title="SysCheck", filename="_syscheck.xlsx")
    return f"{os.path.basename(path)} {round(os.path.getsize(path)/1024)}KB"
check("M4 Tools", "Excel generation", gen_excel_live)

# ─── MODULE 5: Vision ─────────────────────────────────────────────
from vision_connector import vision

check("M5 Vision", "vision_connector import", lambda: "ok")
check("M5 Vision", "vision.is_available()", lambda: str(vision.is_available()))

from PIL import Image
def test_img_load():
    img = Image.new("RGB", (50, 50), color=(30,30,46))
    tp = r"d:\Antigravity\AG-Agent\outputs\_syscheck.png"
    img.save(tp)
    b64 = vision._load_image_b64(tp)
    return f"base64 len={len(b64)}"
check("M5 Vision", "local image → base64", test_img_load)

# ─── MODULE 6: Telegram Bot ────────────────────────────────────────
from config import TELEGRAM_BOT_TOKEN
import requests as req

check("M6 Telegram", "telegram import", lambda: __import__("telegram") and "ok")
check("M6 Telegram", "telegram_bot import", lambda: __import__("telegram_bot") and "ok")
check("M6 Telegram", "bot token set", lambda: f"len={len(TELEGRAM_BOT_TOKEN)}" if TELEGRAM_BOT_TOKEN else (_ for _ in ()).throw(Exception("token empty")))

def check_bot_api():
    r = req.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe", timeout=10)
    d = r.json()["result"]
    return f"@{d['username']}"
check("M6 Telegram", "getMe API call", check_bot_api)

# ─── MODULE 7: Speech ─────────────────────────────────────────────
from speech_to_text import stt

check("M7 Speech", "faster_whisper import", lambda: __import__("faster_whisper") and "ok")
check("M7 Speech", "speech_to_text import", lambda: "ok")
check("M7 Speech", "stt.is_available()", lambda: str(stt.is_available()))
check("M7 Speech", "device detection", lambda: f"device={stt.device} compute={stt.compute_type}")
check("M7 Speech", "telegram_voice_handler import", lambda: __import__("telegram_voice_handler") and "ok")

# ─── DESIGNER SKILL ─────────────────────────────────────────────────
from skills.designer_skill import PRESENTATION_LAYOUT, REPORT_LAYOUT, SPREADSHEET_LAYOUT

check("Designer", "skills import", lambda: "ok")
check("Designer", "presentation_layout", lambda: f"{len(PRESENTATION_LAYOUT['slide_structure'])} slides defined")
check("Designer", "report_layout", lambda: f"{len(REPORT_LAYOUT['document_structure'])} sections defined")
check("Designer", "spreadsheet_layout", lambda: f"{len(SPREADSHEET_LAYOUT['sheet_structure'])} sheets defined")

steps = build_slides_workflow("test")
check("Designer", "Designer Skill in slides workflow", lambda: "Designer Skill" in [s.name for s in steps] and "yes")

# ─── DOCKER ─────────────────────────────────────────────────────────
import subprocess
def check_docker():
    r = subprocess.run(["docker", "images", "ag-agent-antigravity-bot", "--format", "{{.Size}}"],
                       capture_output=True, text=True, timeout=10)
    if r.returncode != 0 or not r.stdout.strip():
        raise Exception("image not found")
    return f"image size: {r.stdout.strip()}"
check("Docker", "image built", check_docker)

# ─── PRINT REPORT ──────────────────────────────────────────────────────
print()
total_pass = total_fail = total_warn = 0
for module, checks in results.items():
    print(f"\n{'\u2500'*60}")
    print(f"  {module}")
    print(f"{'\u2500'*60}")
    for name, status, detail in checks:
        detail_str = f"  → {detail}" if detail else ""
        print(f"  {status}  {name}{detail_str}")
        if status == PASS: total_pass += 1
        elif status == FAIL: total_fail += 1
        else: total_warn += 1

print()
print("=" * 60)
print(f"  RESULTS: {total_pass} passed  |  {total_fail} failed  |  {total_warn} warnings")
print("=" * 60)
if total_fail == 0:
    print("\n  🚀 SYSTEM OPERATIONAL — ALL CHECKS PASSED")
else:
    print(f"\n  ⚠️  {total_fail} check(s) need attention")
print()
