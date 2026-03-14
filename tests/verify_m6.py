"""Module 6 Verification — Telegram Bot."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 6 Verification ===\n")

failures = []

def check(name, fn):
    try:
        r = fn()
        print(f"OK  {name}" + (f": {r}" if r else ""))
    except Exception as e:
        print(f"FAIL {name}: {e}")
        failures.append(name)

check("telegram import", lambda: __import__("telegram"))
check("telegram.ext import", lambda: __import__("telegram.ext", fromlist=["Application"]))
check("telegram_bot module", lambda: __import__("telegram_bot"))

from config import TELEGRAM_BOT_TOKEN
has_token = bool(TELEGRAM_BOT_TOKEN and len(TELEGRAM_BOT_TOKEN) > 10)
check("Telegram token in .env", lambda: f"set={has_token}, len={len(TELEGRAM_BOT_TOKEN)}")

from telegram_bot import startup_check
check("startup_check()", lambda: startup_check()[:60])

import requests, os
from dotenv import load_dotenv
load_dotenv(r"d:\Antigravity\AG-Agent\.env")
token = os.getenv("TELEGRAM_BOT_TOKEN", "")
if token:
    def test_token():
        resp = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        if resp.status_code == 200:
            bot = resp.json()["result"]
            return f"@{bot['username']} — {bot['first_name']}"
        return f"HTTP {resp.status_code}"
    check("Bot token valid (getMe)", test_token)

print()
if failures:
    print(f"FAILURES: {failures}")
else:
    print("=== All checks passed! ===")
