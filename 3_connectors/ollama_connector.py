# ============================================================
# ollama_connector.py — Antigravity Multi-Agent System
# Wrapper around the Ollama local API
# ============================================================

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import requests
import json
from config import OLLAMA_BASE_URL


class OllamaConnector:
    def __init__(self, base_url: str = OLLAMA_BASE_URL):
        self.base_url = base_url

    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def chat(self, model: str, messages: list, temperature: float = 0.2) -> str:
        """
        Send a chat request to Ollama.

        Args:
            model: Model name (e.g. 'qwen2.5:7b')
            messages: List of dicts with 'role' and 'content'
            temperature: Sampling temperature

        Returns:
            Assistant's response as a string
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }

        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]

        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "❌ Cannot connect to Ollama. Make sure it's running with: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("❌ Ollama request timed out. The model may be loading.")
        except (KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"❌ Unexpected response from Ollama: {e}")

    def generate(self, model: str, prompt: str, temperature: float = 0.2,
                 history: list = None) -> str:
        """
        Generate a response, optionally with prior conversation history.

        Args:
            model:       Model name (e.g. 'qwen2.5:7b')
            prompt:      The current user message
            temperature: Sampling temperature
            history:     Optional list of prior messages
                         [{"role": "user"|"assistant", "content": "..."}]
                         These are prepended before the current prompt.

        Returns:
            Generated text as a string
        """
        messages = list(history) if history else []
        messages.append({"role": "user", "content": prompt})
        return self.chat(model, messages, temperature)

    def list_models(self) -> list:
        """Return list of locally available model names."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []


# Singleton instance for use across modules
ollama = OllamaConnector()
