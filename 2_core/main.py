# ============================================================
# main.py — Antigravity Multi-Agent System
# CLI entry point — interactive loop for all modules
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402
from ollama_connector import ollama
from anythingllm_connector import anythingllm
from vision_connector import vision
from workflow_engine import engine
from research_workflow import build_research_workflow, build_slides_workflow, build_qa_workflow
from router import route, describe_route, select_model
from config import REASONING_MODEL, VISION_MODEL, MEDICAL_MODEL


ANTIGRAVITY_BANNER = """
╔══════════════════════════════════════════════════╗
║        🚀 ANTIGRAVITY AI AGENT — v0.2            ║
║        Module 1+2: Router + Ollama + RAG         ║
╚══════════════════════════════════════════════════╝
Type your request and press Enter.
Commands:
  'models'      → list Ollama models
  'workspaces'  → list AnythingLLM workspaces
  'quit/exit'   → stop
─────────────────────────────────────────────────────
"""


def handle_ollama_task(route_result: dict, user_input: str) -> str:
    task = route_result.get("task", "general_reasoning")
    params = route_result.get("parameters", {})

    if task == "generate_slides":
        topic = params.get("topic", user_input)
        print(f"\n🎤 Starting slide generation workflow for: {topic}\n")
        result = engine.run("Generate Slides", steps=build_slides_workflow(topic))
        return result.context.get("run_designer", result.context.get("slide_prompt", "[no output]"))

    elif task == "research_report":
        topic = params.get("topic", user_input)
        print(f"\n🔬 Starting research workflow for: {topic}\n")
        result = engine.run("Research Report", steps=build_research_workflow(topic))
        return result.context.get("generate_summary", "[no output]")

    else:
        model = select_model(route_result)
        domain = "🩺 MedGemma" if route_result.get("is_medical") else "🧠 Qwen"
        print(f"\n⏳ Sending to Ollama [{domain}]...\n")
        return ollama.generate(model=model, prompt=user_input)


def handle_anythingllm_task(route_result: dict, user_input: str) -> str:
    print("\n⏳ Querying AnythingLLM knowledge base...\n")

    if not anythingllm.api_key:
        return (
            "⚠️  AnythingLLM API key not set.\n"
            "   → Open .env and set ANYTHINGLLM_API_KEY=your-key"
        )

    params = route_result.get("parameters", {})
    query = params.get("query", user_input)
    task = route_result.get("task", "knowledge_query")

    if task in ("knowledge_query", "qa"):
        result = engine.run("Q&A with RAG", steps=build_qa_workflow(query))
        return result.context.get("refine_answer", result.context.get("query_knowledge_base", "[no output]"))

    return anythingllm.smart_query(query)


def handle_vision_task(route_result: dict, user_input: str) -> str:
    print("\n👁️  Sending to Vision subsystem (MedGemma)...\n")

    task = route_result.get("task", "describe")
    params = route_result.get("parameters", {})
    image_source = params.get("image") or params.get("image_path")

    if not image_source:
        print("📷 This task requires an image.")
        image_source = input("   Enter image path or URL: ").strip()

    if not image_source:
        return "⚠️  No image provided. Please provide a file path or URL."

    if not vision.is_available():
        return (
            f"⚠️  Vision model ({VISION_MODEL}) not loaded in Ollama.\n"
            f"   Run: ollama pull {VISION_MODEL}"
        )

    try:
        return vision.dispatch(task, image_source, params)
    except FileNotFoundError as e:
        return f"❌ Image not found: {e}"
    except Exception as e:
        return f"❌ Vision error: {e}"


def process_request(user_input: str) -> None:
    print("\n🔀 Routing your request...\n")
    route_result = route(user_input)
    print(describe_route(route_result))
    print("─" * 53)

    destination = route_result.get("route", "ollama")

    if destination == "ollama":
        response = handle_ollama_task(route_result, user_input)
        print(f"\n🤖 Ollama Response:\n\n{response}")
    elif destination == "anythingllm":
        response = handle_anythingllm_task(route_result, user_input)
        print(f"\n{response}")
    elif destination == "vision":
        response = handle_vision_task(route_result, user_input)
        print(f"\n{response}")
    else:
        print(f"❓ Unknown route: {destination}. Defaulting to Ollama.")
        response = handle_ollama_task(route_result, user_input)
        print(f"\n🤖 Ollama Response:\n\n{response}")


def main():
    print(ANTIGRAVITY_BANNER)

    if not ollama.is_available():
        print("❌ ERROR: Cannot connect to Ollama. Run: ollama serve")
        sys.exit(1)
    print("✅ Ollama is online.")

    if anythingllm.is_available():
        workspaces = anythingllm.get_workspace_names()
        ws_list = ", ".join(workspaces) if workspaces else "none found"
        print(f"✅ AnythingLLM is online. Workspaces: {ws_list}")
    else:
        print("⚠️  AnythingLLM not reachable (RAG queries will be skipped).")

    if vision.is_available():
        print(f"✅ Vision model ready: {VISION_MODEL}")
    else:
        print(f"⚠️  Vision model not loaded.")
        print(f"   To enable: ollama pull {VISION_MODEL}")

    print()

    while True:
        try:
            user_input = input("\n💬 You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Antigravity shutting down. Goodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("\n👋 Antigravity shutting down. Goodbye!")
            break
        if user_input.lower() == "models":
            models = ollama.list_models()
            print("\n📦 Available Ollama models:")
            for m in models:
                print(f"   • {m}")
            continue
        if user_input.lower() == "workspaces":
            try:
                workspaces = anythingllm.list_workspaces()
                if workspaces:
                    print("\n📚 AnythingLLM Workspaces:")
                    for ws in workspaces:
                        print(f"   • {ws.get('name','?')}  (slug: {ws.get('slug','?')})")
                else:
                    print("\n📚 No workspaces found.")
            except Exception as e:
                print(f"\n❌ Could not fetch workspaces: {e}")
            continue

        process_request(user_input)
        print("\n" + "─" * 53)


if __name__ == "__main__":
    main()
