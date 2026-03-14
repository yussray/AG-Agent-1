# Antigravity AI Agent — v1.0

> A local multi-agent AI system accessible via Telegram, powered by two specialised LLMs, live internet search, RAG knowledge retrieval, and a full document generation toolkit.

---

## 🧠 What It Does

| Capability | How |
|---|---|
| General reasoning & coding | Qwen 2.5:7b via Ollama |
| Medical / clinical questions | MedGemma (auto-routed) |
| Knowledge base Q&A | AnythingLLM RAG |
| Internet search | Tavily API → Playwright → requests fallback |
| Voice messages | faster-whisper (local speech-to-text) |
| Image / X-ray analysis | MedGemma Vision via Ollama |
| Slides / PDF / Excel / Word | Python tool layer |
| Telegram interface | python-telegram-bot |

---

## 📁 Project Structure

```
AG-Agent/
├── 1_config/         # Environment variables, configuration, requirements
├── 2_core/           # Main orchestration: router, workflow engine, CLI
├── 3_connectors/     # API clients: Ollama, AnythingLLM, Vision
├── 4_tools/          # Tool layer: search, scrape, generate docs, images
├── 5_skills/         # Designer skill + layout templates
├── 6_workflows/      # Pre-built workflow definitions
├── 7_interfaces/     # Telegram bot + voice handler + speech-to-text
├── 8_outputs/        # Generated files (PDF, PPTX, DOCX, etc.)
├── 9_docs/           # Documentation
├── paths.py          # Python path bootstrap
├── Dockerfile
└── docker-compose.yml
```

---

See `9_docs/README.md` for full installation and setup instructions.
