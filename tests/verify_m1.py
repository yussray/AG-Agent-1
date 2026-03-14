"""Quick verification of Module 1 — runs without blocking on LLM calls."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 1 Verification ===\n")

try:
    import requests
    print("OK requests library")
except ImportError as e:
    print(f"FAIL requests missing: {e}")
    sys.exit(1)

try:
    import config
    print(f"OK config.py  (ROUTER_MODEL={config.ROUTER_MODEL})")
except Exception as e:
    print(f"FAIL config.py: {e}")

try:
    from ollama_connector import OllamaConnector
    print("OK ollama_connector.py")
    oc = OllamaConnector()
    alive = oc.is_available()
    print(f"OK Ollama server alive: {alive}")
    if alive:
        models = oc.list_models()
        print(f"   Models: {models}")
except Exception as e:
    print(f"FAIL ollama_connector.py: {e}")

try:
    from router import route, describe_route, ROUTER_SYSTEM_PROMPT
    print("OK router.py")
except Exception as e:
    print(f"FAIL router.py: {e}")

print("\n=== Done ===")
