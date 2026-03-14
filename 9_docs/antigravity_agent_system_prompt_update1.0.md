# Antigravity Multi‑Agent System Build Specification

## Objective
Build a local AI orchestration system where user requests from Telegram or an IDE are routed through a Router LLM to specialized subsystems. The system must decide whether to use RAG knowledge retrieval (AnythingLLM), reasoning (Ollama), or vision models, then execute tasks through Antigravity workflows and Python tools.

The goal is to create a modular "AI operating system" capable of automation, research, document generation, vision analysis, and workflow execution.

---

# High Level Architecture

```
Telegram / IDE
      ↓
Router LLM (decision engine)
      ↓
 ┌───────────────┬───────────────┬───────────────┐
 │               │               │
AnythingLLM RAG  Ollama LLM      Vision Models
 │               │               │
 └───────────────┴───────────────┘
        ↓
Antigravity Workflow Engine
        ↓
Python Tool Layer
        ↓
Output Generator
(PDF / Slides / Report / Automation / Screenshot)
```

---

# System Responsibilities

## 1 Router LLM
The Router LLM acts as the command interpreter.

Responsibilities:
- Read incoming user requests
- Classify request intent
- Output structured JSON command
- Decide which subsystem should process the request

Expected JSON format:

```json
{
  "route": "anythingllm | ollama | vision",
  "task": "task_name",
  "is_medical": true,
  "parameters": {}
}
```

---

# 2 Request Routing Logic

| Intent | Route | Task |
|---|---|---|
| Stored documents / knowledge base | anythingllm | knowledge_query |
| Create slides | ollama | generate_slides |
| Research report | ollama | research_report |
| Internet search / URL scrape | ollama | web_search |
| Code generation | ollama | general_reasoning |
| Image / X-ray | vision | medical_image_analysis |
| Medical question | ollama | general_reasoning (MedGemma) |
| General question | ollama | general_reasoning (Qwen) |

---

# 3 AnythingLLM RAG Subsystem

Pipeline:
```
User query → Embedding → Vector search → Relevant chunks → LLM response
```

---

# 4 Ollama Reasoning Subsystem

Models:
- `qwen2.5:7b` — general reasoning
- `dcarrascosa/medgemma-1.5-4b-it:Q8_0` — medical/clinical
- `qwen2.5-coder:7b` — code generation

---

# 5 Vision Subsystem

Capabilities:
- medical image analysis (X-ray, CT, MRI, ultrasound)
- screenshot interpretation
- document OCR
- visual question answering

---

# 6 Designer Skill (Universal Output Polisher)

Purpose: Improve quality and structure of all generated outputs before reaching the tool layer.

Pipeline:
```
User request → Router LLM → Designer Skill → Workflow Engine → Tool Layer → Polished Output
```

Slide structure:
```
Slide 1 — Title
Slide 2 — Overview
Slide 3 — Background
Slide 4 — Key Concepts
Slide 5 — Explanation
Slide 6 — Supporting Example
Slide 7 — Summary
Slide 8 — References
```

Report structure:
```
Title → Executive Summary → Background → Main Analysis → Key Insights → Recommendations → Conclusion → References
```

---

# 7 Module 7 — Speech Interface

Pipeline:
```
Telegram voice message → Download audio → faster-whisper (local STT) → Text → Router LLM → Normal pipeline
```

Files:
- `speech_to_text.py` — Whisper transcription engine
- `telegram_voice_handler.py` — detects voice, downloads audio

---

# Expected Outcome

A local multi-agent AI system capable of:
- reasoning
- knowledge retrieval
- workflow automation
- document creation
- vision analysis

All triggered by a single command interface via Telegram.
