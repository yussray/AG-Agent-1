# ============================================================
# ollama_connector.py — Antigravity Multi-Agent System
# Client wrapper for the Ollama local LLM API
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import requests
import logging
from config import OLLAMA_BASE_URL

logger = logging.getLogger("antigravity.ollama")


class OllamaConnector:
    """
    Thin wrapper around the Ollama REST API.
    Provides chat, generate, and model management functions.
    """

    def __init__(self, base_url: str = None):
        self.base_url = (base_url or OLLAMA_BASE_URL).rstrip("/")

    def is_available(self) -> bool:
        """Check if Ollama is running and reachable."""
        try:
            r = requests.get(f"{self.base_url}/", timeout=3)
            return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Return a list of available model names."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
        except Exception as e:
            logger.error(f"list_models failed: {e}")
            return []

    def generate(
        self,
        model: str,
        prompt: str,
        system: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> str:
        """
        Generate a completion using the /api/generate endpoint.
        Returns the full response as a string.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system:
            payload["system"] = system

        try:
            r = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            r.raise_for_status()
            return r.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"generate failed [{model}]: {e}")
            raise

    def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2048
    ) -> str:
        """
        Chat completion using the /api/chat endpoint.
        messages: list of {role, content} dicts.
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            r = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            r.raise_for_status()
            return r.json()["message"]["content"].strip()
        except Exception as e:
            logger.error(f"chat failed [{model}]: {e}")
            raise


# Singleton instance
ollama = OllamaConnector()
