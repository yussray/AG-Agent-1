# ============================================================
# vision_connector.py — Antigravity Multi-Agent System
# Vision subsystem — routes image analysis tasks to MedGemma
# Handles image paths, URLs, and base64 input
# ============================================================

import sys
import os as _os
sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import os
import re
import base64
import tempfile
import requests as req
from config import OLLAMA_BASE_URL, VISION_MODEL


class VisionConnector:
    """
    High-level vision subsystem connector.
    Routes image tasks to the Ollama vision model (MedGemma).
    """

    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = VISION_MODEL):
        self.base_url = base_url
        self.model = model

    def is_available(self) -> bool:
        """Check if Ollama is running and the vision model is loaded."""
        try:
            resp = req.get(f"{self.base_url}/api/tags", timeout=3)
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            return any(self.model.split(":")[0] in m for m in models)
        except Exception:
            return False

    # ----------------------------------------------------------------
    # Core inference
    # ----------------------------------------------------------------

    def _infer(self, image_b64: str, prompt: str) -> str:
        """Send image + prompt to Ollama vision model."""
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_b64]
                }
            ],
            "stream": False,
            "options": {"temperature": 0.1}
        }
        resp = req.post(f"{self.base_url}/api/chat", json=payload, timeout=180)
        resp.raise_for_status()
        return resp.json()["message"]["content"]

    # ----------------------------------------------------------------
    # Input normalisation
    # ----------------------------------------------------------------

    def _load_image_b64(self, source: str) -> str:
        """
        Accept a file path, URL, or raw base64 string.
        Returns base64-encoded image string.
        """
        # Already base64
        if len(source) > 200 and not os.path.exists(source) and not source.startswith("http"):
            return source

        # URL — download to temp file
        if source.startswith("http://") or source.startswith("https://"):
            resp = req.get(source, timeout=15)
            resp.raise_for_status()
            ext = source.split(".")[-1].split("?")[0][:4] or "jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as f:
                f.write(resp.content)
                path = f.name
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()

        # File path
        if not os.path.exists(source):
            raise FileNotFoundError(f"Image not found: {source}")
        with open(source, "rb") as f:
            return base64.b64encode(f.read()).decode()

    # ----------------------------------------------------------------
    # Task-specific analysis methods
    # ----------------------------------------------------------------

    def describe(self, image_source: str) -> str:
        """General image description."""
        b64 = self._load_image_b64(image_source)
        return self._infer(b64, "Describe this image in comprehensive detail.")

    def analyze_medical(self, image_source: str) -> str:
        """Medical image analysis (X-ray, CT, MRI, ultrasound, etc.)"""
        b64 = self._load_image_b64(image_source)
        prompt = (
            "You are a medical AI assistant analysing a medical image.\n\n"
            "Provide:\n"
            "1. Image type (X-ray, CT, MRI, ultrasound, etc.)\n"
            "2. Anatomical region\n"
            "3. Key findings and observations\n"
            "4. Notable abnormalities or areas of concern\n"
            "5. Impression / summary\n\n"
            "⚠️  For educational/assistance purposes only — not a clinical diagnosis."
        )
        return self._infer(b64, prompt)

    def extract_text(self, image_source: str) -> str:
        """OCR — extract all text from an image."""
        b64 = self._load_image_b64(image_source)
        prompt = (
            "Extract ALL text visible in this image exactly as it appears.\n"
            "Preserve formatting, line breaks, and table structure.\n"
            "Output only the extracted text, nothing else."
        )
        return self._infer(b64, prompt)

    def analyze_screenshot(self, image_source: str) -> str:
        """Understand a screenshot's content and layout."""
        b64 = self._load_image_b64(image_source)
        prompt = (
            "Analyse this screenshot:\n"
            "1. What application/website is shown?\n"
            "2. Main content visible\n"
            "3. Important text, data, or UI elements\n"
            "4. Summary of what was captured"
        )
        return self._infer(b64, prompt)

    def custom(self, image_source: str, prompt: str) -> str:
        """Custom prompt for any image analysis task."""
        b64 = self._load_image_b64(image_source)
        return self._infer(b64, prompt)

    def medical_analysis(self, image_source: str, clinical_context: str = "") -> str:
        """Medical analysis with optional clinical context."""
        b64 = self._load_image_b64(image_source)
        context_text = f"\n\nClinical context: {clinical_context}" if clinical_context else ""
        prompt = (
            "You are a medical AI assistant analysing a medical image.\n\n"
            "Provide:\n"
            "1. Image type (X-ray, CT, MRI, ultrasound, etc.)\n"
            "2. Anatomical region\n"
            "3. Key findings and observations\n"
            "4. Notable abnormalities or areas of concern\n"
            "5. Impression / summary\n\n"
            "⚠️  For educational/assistance purposes only — not a clinical diagnosis."
            + context_text
        )
        return self._infer(b64, prompt)

    # ----------------------------------------------------------------
    # Router-facing dispatch
    # ----------------------------------------------------------------

    def dispatch(self, task: str, image_source: str, params: dict = None,
                 prompt_override: str = None) -> str:
        """
        Dispatch a vision task based on task name from the router.

        Args:
            task:            Task name from router JSON (e.g. 'medical_image_analysis')
            image_source:    Image path, URL, or base64
            params:          Optional router parameters dict
            prompt_override: If provided, used as the prompt directly

        Returns:
            Analysis text
        """
        params = params or {}

        # If conversation context was injected, use custom prompt mode
        if prompt_override:
            return self.custom(image_source, prompt_override)

        dispatch_map = {
            "medical_image_analysis": self.analyze_medical,
            "medical_analysis": self.medical_analysis,
            "ocr": self.extract_text,
            "extract_text": self.extract_text,
            "screenshot_analysis": self.analyze_screenshot,
            "describe": self.describe,
        }

        if task in dispatch_map:
            fn = dispatch_map[task]
            if task == "medical_analysis":
                return fn(image_source, params.get("clinical_context", ""))
            return fn(image_source)

        # Custom prompt if provided
        custom_prompt = params.get("prompt")
        if custom_prompt:
            return self.custom(image_source, custom_prompt)

        # Default: general description
        return self.describe(image_source)


# Singleton instance
vision = VisionConnector()
