# ============================================================
# config.py — Antigravity Multi-Agent System
# Central configuration for all modules
# Loads secrets from .env file
# ============================================================

import os
from dotenv import load_dotenv

# Load .env from 1_config/ directory (where this file lives)
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_HERE, ".env"))

# --- Ollama ---
# Override OLLAMA_HOST for Docker (host.docker.internal) or remote servers
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")

# Model used to classify/route user intent
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "qwen2.5:7b")

# Model used for general reasoning, writing, planning
REASONING_MODEL = os.getenv("REASONING_MODEL", "qwen2.5:7b")

# Model used for code generation tasks
CODER_MODEL = os.getenv("CODER_MODEL", "qwen2.5-coder:7b")

# Model used for embeddings (AnythingLLM RAG)
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# --- Vision ---
VISION_MODEL = os.getenv("VISION_MODEL", "dcarrascosa/medgemma-1.5-4b-it:Q8_0")

# --- Medical Reasoning ---
# Used when the router detects a medical/clinical request
MEDICAL_MODEL = os.getenv("MEDICAL_MODEL", "dcarrascosa/medgemma-1.5-4b-it:Q8_0")

# --- AnythingLLM ---
# Override ANYTHINGLLM_HOST for Docker or remote servers
ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_HOST", "http://localhost:3001")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "")

# --- Tavily Search ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Memory ---
# Number of messages (not turns) to keep in short-term memory per user.
# 20 = 10 full back-and-forth exchanges.
MEMORY_WINDOW_SIZE = int(os.getenv("MEMORY_WINDOW_SIZE", "20"))

# --- Whisper ---
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# --- Output ---
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "8_outputs")
