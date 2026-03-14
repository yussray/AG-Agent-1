"""Quick verification of Module 2 — AnythingLLM connector."""
import sys
sys.path.insert(0, r"d:\Antigravity\AG-Agent")

print("=== Antigravity Module 2 Verification ===\n")

try:
    from dotenv import load_dotenv
    print("OK python-dotenv")
except ImportError as e:
    print(f"FAIL python-dotenv: {e}")
    sys.exit(1)

try:
    import config
    has_key = bool(config.ANYTHINGLLM_API_KEY and config.ANYTHINGLLM_API_KEY != "")
    print(f"OK config.py  (API key set: {has_key})")
except Exception as e:
    print(f"FAIL config.py: {e}")

try:
    from anythingllm_connector import AnythingLLMConnector
    print("OK anythingllm_connector.py")
except Exception as e:
    print(f"FAIL anythingllm_connector.py: {e}")
    sys.exit(1)

try:
    conn = AnythingLLMConnector()
    alive = conn.is_available()
    print(f"OK AnythingLLM server alive: {alive}")
    if alive and conn.api_key:
        workspaces = conn.list_workspaces()
        print(f"OK Workspaces found: {len(workspaces)}")
        for ws in workspaces:
            print(f"   • {ws.get('name')}  (slug: {ws.get('slug')})")
    elif not conn.api_key:
        print("   API key not yet set in .env — skipping workspace list")
except Exception as e:
    print(f"WARN AnythingLLM: {e}")

try:
    import importlib, main
    print("OK main.py (v0.2 integration)")
except Exception as e:
    print(f"FAIL main.py: {e}")

print("\n=== Done ===")
