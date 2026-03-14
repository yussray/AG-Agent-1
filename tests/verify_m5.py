"""Module 5 Verification — Vision Subsystem."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 5 Verification ===\n")

failures = []

def check(name, fn):
    try:
        result = fn()
        print(f"OK  {name}" + (f": {result}" if result else ""))
    except Exception as e:
        print(f"FAIL {name}: {e}")
        failures.append(name)

check("vision_connector import", lambda: __import__("vision_connector", fromlist=["vision"]))

from vision_connector import VisionConnector, vision
check("VisionConnector instantiate", lambda: VisionConnector())
check("Vision model available", lambda: str(vision.is_available()))

def test_img_load():
    import requests
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
    b64 = vision._load_image_b64(url)
    assert len(b64) > 100, "base64 too short"
    return f"base64 len={len(b64)}"
check("URL image → base64", test_img_load)

check("main.py import", lambda: __import__("main"))

print()
if failures:
    print(f"FAILURES: {failures}")
else:
    print("=== All checks passed! ===")
