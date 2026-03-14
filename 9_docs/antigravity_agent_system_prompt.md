# Antigravity Multi-Agent System — Build Specification

## Objective
Build a local AI orchestration system where user requests from Telegram are routed through a Router LLM to specialised subsystems. The system decides whether to use RAG knowledge retrieval (AnythingLLM), reasoning (Ollama), or vision models, then executes tasks through workflows and Python tools.

---

## High Level Architecture

```
Telegram / IDE
      ↓
Router LLM (decision engine)
      ↓
 ┌───────────────┬───────────────┬───────────────┐
 │               │               │               │
AnythingLLM RAG  Ollama LLM      Vision Models
 │               │               │               │
 └───────────────┴───────────────┘
        ↓
Antigravity Workflow Engine
        ↓
Python Tool Layer
        ↓
Output Generator (PDF / Slides / Report / etc.)
```

---

## Request Routing Logic

| User intent | Route | Task |
|---|---|---|
| Uploaded docs / knowledge base query | anythingllm | knowledge_query |
| Create slides | ollama | generate_slides |
| Research report | ollama | research_report |
| Internet search / URL scrape | ollama | web_search |
| Code generation | ollama | code_generation |
| Image / X-ray analysis | vision | medical_analysis / describe |
| Medical/clinical question | ollama (MedGemma) | general_reasoning |
| Everything else | ollama (Qwen) | general_reasoning |

---

## Speech Interface (Module 7)

```
Telegram voice message
      ↓
Download audio file (.ogg)
      ↓
faster-whisper (local STT)
      ↓
Converted text
      ↓
Router LLM → normal agent pipeline
```
