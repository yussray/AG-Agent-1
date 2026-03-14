# ============================================================
# router.py — Antigravity Multi-Agent System
# Intent classifier — routes user requests to the right subsystem
# Also selects the best LLM model based on domain (medical vs general)
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import json
import re
from ollama_connector import ollama
from config import ROUTER_MODEL, REASONING_MODEL, MEDICAL_MODEL


ROUTER_SYSTEM_PROMPT = """You are a request router for an AI system. Your only job is to classify the user's request and output a JSON routing command.

You must output ONLY valid JSON, nothing else. No explanation, no markdown, no extra text.

Routes available:
- "ollama" → general reasoning, writing, planning, code generation, slide creation, research summaries, web search
- "anythingllm" → queries about stored documents, knowledge base, uploaded research papers
- "vision" → analyzing images, X-rays, screenshots, photos

Task names for ollama route:
- "generate_slides" → user wants a presentation or slideshow
- "research_report" → user wants a research report or detailed write-up
- "web_search" → user wants to search the internet, look up current info, scrape a URL, or find something online
- "general_reasoning" → everything else (questions, writing, coding, explanations)

Medical detection:
- Set "is_medical": true when the request involves medicine, healthcare, clinical topics, anatomy,
  pharmacology, diseases, symptoms, diagnoses, treatments, surgery, radiology, or patient care.
- Set "is_medical": false for all other topics.

JSON format:
{
  "route": "ollama" | "anythingllm" | "vision",
  "task": "short_task_name",
  "is_medical": true | false,
  "parameters": {}
}

Examples:
User: "Create slides about bariatric surgery"
{"route": "ollama", "task": "generate_slides", "is_medical": true, "parameters": {"topic": "bariatric surgery"}}

User: "Search the web for latest diabetes treatment guidelines"
{"route": "ollama", "task": "web_search", "is_medical": true, "parameters": {"query": "latest diabetes treatment guidelines"}}

User: "Scrape this website: https://example.com"
{"route": "ollama", "task": "web_search", "is_medical": false, "parameters": {"url": "https://example.com"}}

User: "What is the mechanism of metformin?"
{"route": "ollama", "task": "general_reasoning", "is_medical": true, "parameters": {}}

User: "Write a Python script to scrape stock prices"
{"route": "ollama", "task": "general_reasoning", "is_medical": false, "parameters": {}}

User: "Summarize my uploaded research papers"
{"route": "anythingllm", "task": "knowledge_query", "is_medical": false, "parameters": {"query": "summarize research papers"}}

User: "Analyze this X-ray"
{"route": "vision", "task": "medical_image_analysis", "is_medical": true, "parameters": {"image": "uploaded_file"}}

Now classify the user's request."""


def extract_json(text: str) -> dict:
    """Try to extract a JSON object from the model's response."""
    # Direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Find JSON block inside text using regex
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def select_model(route_result: dict) -> str:
    """
    Choose the best Ollama model based on the routing result.

    - Medical / clinical topics  → MedGemma
    - Everything else            → Qwen (REASONING_MODEL)
    """
    if route_result.get("is_medical", False):
        return MEDICAL_MODEL
    return REASONING_MODEL


def route(user_input: str) -> dict:
    """
    Classify the user's request and return a routing JSON dict.

    Args:
        user_input: Raw user message

    Returns:
        dict with keys: route, task, is_medical, parameters
    """
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": user_input}
    ]

    raw_response = ollama.chat(
        model=ROUTER_MODEL,
        messages=messages,
        temperature=0.1  # Low temperature for consistent classification
    )

    result = extract_json(raw_response)

    if result is None:
        # Fallback — default to ollama reasoning if we can't parse
        print(f"⚠️  Could not parse router JSON. Raw response:\n{raw_response}")
        result = {
            "route": "ollama",
            "task": "general_reasoning",
            "is_medical": False,
            "parameters": {"prompt": user_input}
        }

    return result


def describe_route(route_result: dict) -> str:
    """Return a human-readable description of the routing decision."""
    icons = {
        "ollama": "🤖",
        "anythingllm": "📚",
        "vision": "👁️"
    }
    is_medical = route_result.get("is_medical", False)
    model_used = select_model(route_result)
    model_label = "🩺 MedGemma" if is_medical else f"🧠 {model_used.split(':')[0]}"
    icon = icons.get(route_result.get("route", ""), "❓")

    return (
        f"{icon} Route    : {route_result.get('route', 'unknown')}\n"
        f"   Task     : {route_result.get('task', 'unknown')}\n"
        f"   Model    : {model_label}  (medical={is_medical})\n"
        f"   Params   : {route_result.get('parameters', {})}"
    )
