# ============================================================
# router.py — Antigravity Multi-Agent System
# Classifies user intent and routes to the right subsystem
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import json
import re
import logging

from ollama_connector import ollama
from config import ROUTER_MODEL, REASONING_MODEL, MEDICAL_MODEL, CODER_MODEL

logger = logging.getLogger("antigravity.router")

# ----------------------------------------------------------------
# Router system prompt
# ----------------------------------------------------------------

ROUTER_SYSTEM_PROMPT = """
You are a routing AI. Classify the user request and output ONLY valid JSON.

Routes:
- "ollama"       — reasoning, writing, code, slides, reports, web search
- "anythingllm"  — knowledge base queries about uploaded documents
- "vision"       — image analysis, OCR, medical imaging

Tasks (for ollama route):
- "general_reasoning"  — default
- "generate_slides"    — create presentation slides
- "research_report"    — write a structured research report
- "web_search"         — internet search or scrape a URL
- "code_generation"    — write or explain code

Tasks (for vision route):
- "describe"           — general image description
- "medical_analysis"   — medical/clinical image analysis
- "ocr"                — extract text from image
- "screenshot"         — analyse a screenshot

Required JSON format:
{
  "route": "ollama | anythingllm | vision",
  "task": "task_name",
  "is_medical": true | false,
  "parameters": {
    "topic": "...",
    "query": "...",
    "url": "..."
  }
}

Rules:
- If the request mentions X-ray, MRI, scan, medical image → route=vision, task=medical_analysis
- If the request mentions documents, research papers, knowledge base → route=anythingllm
- If the request mentions a URL to scrape or search online → route=ollama, task=web_search
- is_medical=true for any clinical, medical, or healthcare topic
- Output ONLY the JSON object. No explanation.
"""


# ----------------------------------------------------------------
# Core routing function
# ----------------------------------------------------------------

def route(user_input: str) -> dict:
    """
    Route a user request to the correct subsystem.

    Returns:
        dict with keys: route, task, is_medical, parameters
    """
    prompt = f"User request: {user_input}"

    try:
        raw = ollama.chat(
            model=ROUTER_MODEL,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user",   "content": prompt}
            ]
        )

        # Extract JSON from response
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
            # Normalise keys
            result.setdefault("route", "ollama")
            result.setdefault("task", "general_reasoning")
            result.setdefault("is_medical", False)
            result.setdefault("parameters", {})
            return result

    except Exception as e:
        logger.warning(f"Router LLM failed: {e}. Using fallback routing.")

    # Fallback: keyword-based routing
    return _fallback_route(user_input)


def _fallback_route(user_input: str) -> dict:
    """Simple keyword-based fallback routing."""
    text = user_input.lower()

    is_medical = any(kw in text for kw in [
        "medical", "clinical", "patient", "surgery", "diagnosis",
        "treatment", "hospital", "disease", "doctor", "health",
        "bariatric", "obesity", "x-ray", "mri", "scan"
    ])

    # Vision
    if any(kw in text for kw in ["image", "photo", "picture", "x-ray", "mri", "scan", "analyze", "describe"]):
        task = "medical_analysis" if is_medical else "describe"
        return {"route": "vision", "task": task, "is_medical": is_medical, "parameters": {}}

    # RAG
    if any(kw in text for kw in ["document", "research paper", "knowledge base", "uploaded", "summarize my"]):
        return {"route": "anythingllm", "task": "knowledge_query", "is_medical": is_medical, "parameters": {"query": user_input}}

    # Slides
    if any(kw in text for kw in ["slide", "presentation", "pptx", "powerpoint"]):
        topic = user_input
        for prefix in ["create slides about", "make slides about", "slides on", "slides about"]:
            if prefix in text:
                topic = user_input[text.index(prefix) + len(prefix):].strip()
                break
        return {"route": "ollama", "task": "generate_slides", "is_medical": is_medical, "parameters": {"topic": topic}}

    # Web search
    if any(kw in text for kw in ["search", "google", "look up", "find online", "http", "www."]):
        return {"route": "ollama", "task": "web_search", "is_medical": is_medical, "parameters": {"query": user_input}}

    # Code
    if any(kw in text for kw in ["code", "script", "function", "python", "javascript", "program"]):
        return {"route": "ollama", "task": "code_generation", "is_medical": False, "parameters": {}}

    return {"route": "ollama", "task": "general_reasoning", "is_medical": is_medical, "parameters": {}}


# ----------------------------------------------------------------
# Model selection
# ----------------------------------------------------------------

def select_model(route_result: dict) -> str:
    """Select the best Ollama model for a route result."""
    task = route_result.get("task", "general_reasoning")
    is_medical = route_result.get("is_medical", False)

    if is_medical:
        return MEDICAL_MODEL
    if task == "code_generation":
        return CODER_MODEL
    return REASONING_MODEL


def describe_route(route_result: dict) -> str:
    """Return a human-readable description of the routing decision."""
    route = route_result.get("route", "?")
    task = route_result.get("task", "?")
    is_medical = route_result.get("is_medical", False)
    params = route_result.get("parameters", {})

    icon = {
        "ollama": "🧠", "anythingllm": "📚", "vision": "👁️"
    }.get(route, "❔")

    lines = [
        f"{icon} Route    : {route}",
        f"   Task    : {task}",
        f"   Medical : {is_medical}",
    ]
    if params:
        for k, v in params.items():
            lines.append(f"   {k:<8}: {v}")
    return "\n".join(lines)
