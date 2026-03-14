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

## 🖥️ Required Software

Install in this exact order:

### 1. Git
- Download: https://git-scm.com/downloads
- Verify: `git --version`

### 2. Docker Desktop
- Download: https://www.docker.com/products/docker-desktop
- Enable WSL 2 backend during setup (Windows)
- Verify: `docker --version`

### 3. Ollama
- Download: https://ollama.com/download
- Verify: `ollama --version`

### 4. AnythingLLM Desktop
- Download: https://useanything.com
- Run it — it starts at `http://localhost:3001`

---

## 🔑 API Keys Required

| Key | Where to get |
|---|---|
| `TELEGRAM_BOT_TOKEN` | [@BotFather](https://t.me/BotFather) on Telegram |
| `ANYTHINGLLM_API_KEY` | AnythingLLM → Settings → API Keys |
| `TAVILY_API_KEY` | https://app.tavily.com → API Keys |

---

## ⚙️ Installation Sequence

### Step 1 — Pull the required Ollama models
```bash
ollama pull qwen2.5:7b
ollama pull dcarrascosa/medgemma-1.5-4b-it:Q8_0
ollama pull nomic-embed-text
```
> First-time download ~10GB. Cached after that.

### Step 2 — Clone the project
```bash
git clone https://github.com/yussray/AG-Agent-1.git AG-Agent
cd AG-Agent
```

### Step 3 — Configure environment variables
```bash
cp 1_config/.env.example 1_config/.env
```
Edit `1_config/.env`:
```
ANYTHINGLLM_API_KEY=your-key-here
TELEGRAM_BOT_TOKEN=your-token-here
TAVILY_API_KEY=your-tavily-key-here
```

### Step 4 — Set up AnythingLLM
1. Open AnythingLLM Desktop
2. Go to **Settings → LLM** → select Ollama → model: `qwen2.5:7b`
3. Go to **Settings → Embedder** → select Ollama → model: `nomic-embed-text`
4. Create a workspace (e.g., "Medical Knowledge")
5. Upload your documents and copy your API key into `.env`

### Step 5 — Build and start
```bash
docker compose up -d --build
```
> First build ~5–8 minutes. Subsequent restarts ~3 seconds.

### Step 6 — Test the bot
Open Telegram → find your bot → send:
```
/start
/status
What are the complications of laparoscopic cholecystectomy?
Create slides about bariatric surgery
```

---

## 🗂️ Project Structure

```
AG-Agent/
├── 1_config/           # Environment & settings
├── 2_core/             # Router, workflow engine, CLI
├── 3_connectors/       # Ollama, AnythingLLM, Vision clients
├── 4_tools/            # Search, scraping, document generation
├── 5_skills/           # Designer skill + layout templates
├── 6_workflows/        # Pre-built workflow definitions
├── 7_interfaces/       # Telegram bot + voice + STT
├── 8_outputs/          # Generated files (Docker volume)
├── 9_docs/             # Documentation
├── paths.py            # sys.path bootstrap
├── Dockerfile
└── docker-compose.yml
```

---

## 🔄 Routing Logic

Every message is classified by the Router LLM (Qwen):

| User intent | Route | Model |
|---|---|---|
| Uploaded docs / knowledge base | anythingllm | RAG |
| Create slides | ollama | Qwen / MedGemma |
| Research report | ollama | Qwen |
| Internet search | ollama | Qwen |
| Code generation | ollama | Qwen Coder |
| Image / X-ray | vision | MedGemma Vision |
| Medical question | ollama | MedGemma |
| General question | ollama | Qwen |

---

## 📦 Docker Quick Reference

| Command | Action |
|---|---|
| `docker compose up -d --build` | Build and start |
| `docker compose up -d` | Start (no rebuild) |
| `docker compose down` | Stop |
| `docker compose logs -f` | Live logs |

---

## ⚠️ Troubleshooting

| Issue | Fix |
|---|---|
| Bot not responding | Check `docker compose logs` |
| Ollama offline | Run `ollama serve` |
| AnythingLLM offline | Open AnythingLLM Desktop app |
| Model not found | Run `ollama pull <model-name>` |
| RAG not working | Check `ANYTHINGLLM_API_KEY` in `.env` |
| Web search failing | Check `TAVILY_API_KEY` in `.env` |

---

*Built on: Ollama · AnythingLLM · Tavily · Playwright · python-telegram-bot · Docker*
