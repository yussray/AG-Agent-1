"""Module 7 Verification — Speech Interface."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 7 Verification ===\n")
failures = []

def check(name, fn):
    try:
        r = fn()
        print(f"OK  {name}" + (f": {str(r)[:80]}" if r else ""))
    except Exception as e:
        print(f"FAIL {name}: {e}")
        failures.append(name)

check("faster_whisper import", lambda: __import__("faster_whisper"))
check("speech_to_text import", lambda: __import__("speech_to_text", fromlist=["stt"]))

from speech_to_text import stt
check("stt.is_available()", lambda: str(stt.is_available()))
check("Device detection", lambda: f"device={stt.device}, compute={stt.compute_type}")
check("telegram_voice_handler", lambda: __import__("telegram_voice_handler", fromlist=["handle_voice_message"]))

import ast
with open(r"d:\Antigravity\AG-Agent\telegram_bot.py", encoding="utf-8") as f:
    src = f.read()
def check_syntax():
    ast.parse(src)
    return "syntax OK"
check("telegram_bot.py syntax", check_syntax)

check("telegram_bot import", lambda: __import__("telegram_bot"))

from telegram_bot import main
import inspect
src_main = inspect.getsource(main)
check("Voice handler registered", lambda: "VOICE" in src_main and "handle_voice_message" in src_main)

from telegram_bot import startup_check
status = startup_check()
check("startup_check includes STT", lambda: "Speech-to-text" in status and status[:60])

print()
if failures:
    print(f"FAILURES: {failures}")
else:
    print("=== All checks passed! ===")
