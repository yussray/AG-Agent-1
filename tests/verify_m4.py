"""Module 4 Verification — imports + generate sample PPT and PDF."""
import sys, os
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 4 Verification ===\n")

failures = []

def check(name, fn):
    try:
        fn()
        print(f"OK  {name}")
    except Exception as e:
        print(f"FAIL {name}: {e}")
        failures.append(name)

check("tools/make_slides", lambda: __import__("tools.make_slides", fromlist=["make_slides"]))
check("tools/make_pdf",    lambda: __import__("tools.make_pdf",    fromlist=["make_pdf"]))
check("tools/make_word",   lambda: __import__("tools.make_word",   fromlist=["make_word"]))
check("tools/make_excel",  lambda: __import__("tools.make_excel",  fromlist=["make_excel"]))
check("tools/export_csv",  lambda: __import__("tools.export_csv",  fromlist=["export_csv"]))
check("tools/web_scraper", lambda: __import__("tools.web_scraper", fromlist=["scrape_url"]))
check("tools/screenshot_tool", lambda: __import__("tools.screenshot_tool", fromlist=["take_screenshot"]))
check("tools/image_analysis",  lambda: __import__("tools.image_analysis",  fromlist=["analyze_image"]))
check("tools/medical_image_reader", lambda: __import__("tools.medical_image_reader", fromlist=["read_medical_image"]))
check("tools/ocr_reader",  lambda: __import__("tools.ocr_reader",  fromlist=["extract_text_from_image"]))
check("tools/file_reader", lambda: __import__("tools.file_reader", fromlist=["read_text_file"]))
check("tools/file_writer", lambda: __import__("tools.file_writer", fromlist=["write_text_file"]))
check("tools/folder_manager", lambda: __import__("tools.folder_manager", fromlist=["list_folder"]))

print()

SAMPLE_OUTLINE = """
SLIDE 1: Bariatric Surgery Overview
  - Definition and scope
  - Global prevalence of obesity
  - Why surgery is needed

SLIDE 2: Types of Procedures
  - Sleeve gastrectomy
  - Roux-en-Y gastric bypass
  - Adjustable gastric band

SLIDE 3: Patient Selection
  - BMI criteria (>40 or >35 with comorbidities)
  - Psychological evaluation
  - Nutritional assessment

SLIDE 4: Conclusion
  - Surgery is effective and safe
  - Multidisciplinary approach required
  - Long-term follow-up is essential
"""

def gen_pptx():
    from tools.make_slides import make_slides
    path = make_slides(SAMPLE_OUTLINE, title="Bariatric Surgery", filename="test_slides.pptx")
    assert os.path.exists(path)
    print(f"   PPTX: {path}  ({os.path.getsize(path)/1024:.1f} KB)")
check("Generate PPTX", gen_pptx)

def gen_pdf():
    from tools.make_pdf import make_pdf
    content = "## Overview\nBariatric surgery is a treatment for severe obesity.\n- Sleeve gastrectomy\n- Gastric bypass\n\n## Conclusion\nEffective and safe when indicated."
    path = make_pdf(content, title="Bariatric Summary", filename="test_report.pdf")
    assert os.path.exists(path)
    print(f"   PDF:  {path}  ({os.path.getsize(path)/1024:.1f} KB)")
check("Generate PDF", gen_pdf)

def gen_word():
    from tools.make_word import make_word
    path = make_word("## Introduction\nThis is a test Word document.\n- Point 1\n- Point 2", title="Test Doc", filename="test_doc.docx")
    assert os.path.exists(path)
    print(f"   DOCX: {path}  ({os.path.getsize(path)/1024:.1f} KB)")
check("Generate Word", gen_word)

def gen_excel():
    from tools.make_excel import make_excel
    data = [["Name", "BMI", "Procedure", "Outcome"], ["Patient A", 42, "Sleeve", "Success"], ["Patient B", 38, "Bypass", "Success"]]
    path = make_excel(data, title="Patient Data", filename="test_excel.xlsx")
    assert os.path.exists(path)
    print(f"   XLSX: {path}  ({os.path.getsize(path)/1024:.1f} KB)")
check("Generate Excel", gen_excel)

def file_utils():
    from tools.file_writer import write_text_file
    from tools.file_reader import read_text_file, get_file_info
    from tools.folder_manager import get_outputs_summary, list_folder_tree
    path = write_text_file(r"d:\Antigravity\AG-Agent\outputs\test_file.txt", "Hello from Antigravity!")
    content = read_text_file(path)
    assert content == "Hello from Antigravity!"
    info = get_file_info(path)
    print(f"   File: {info['name']}  ({info['size_kb']} KB)")
check("File read/write/folder", file_utils)

print()
if failures:
    print(f"FAILURES: {failures}")
else:
    print("=== All checks passed! ===")
