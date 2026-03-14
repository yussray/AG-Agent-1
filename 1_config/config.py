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
OLLAMA_BASE_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434")
ROUTER_MODEL = os.getenv("ROUTER_MODEL", "qwen2.5:7b")
REASONING_MODEL = os.getenv("REASONING_MODEL", "qwen2.5:7b")
CODER_MODEL = os.getenv("CODER_MODEL", "qwen2.5-coder:7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# --- Vision ---
VISION_MODEL = os.getenv("VISION_MODEL", "dcarrascosa/medgemma-1.5-4b-it:Q8_0")

# --- Medical Reasoning ---
MEDICAL_MODEL = os.getenv("MEDICAL_MODEL", "dcarrascosa/medgemma-1.5-4b-it:Q8_0")

# --- AnythingLLM ---
ANYTHINGLLM_BASE_URL = os.getenv("ANYTHINGLLM_HOST", "http://localhost:3001")
ANYTHINGLLM_API_KEY = os.getenv("ANYTHINGLLM_API_KEY", "")

# --- Tavily Search ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Whisper ---
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# --- Output ---
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "8_outputs")
