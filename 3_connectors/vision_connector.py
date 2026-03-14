# ============================================================
# vision_connector.py — Antigravity Multi-Agent System
# Routes vision tasks to MedGemma via Ollama
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import base64
import logging
import requests

from ollama_connector import ollama
from config import VISION_MODEL, OLLAMA_BASE_URL

logger = logging.getLogger("antigravity.vision")


class VisionConnector:
    """
    Handles image-based tasks using Ollama multimodal models (MedGemma).
    Supports file paths, URLs, and base64-encoded images.
    """

    def __init__(self, model: str = None):
        self.model = model or VISION_MODEL
        self.base_url = OLLAMA_BASE_URL.rstrip("/")

    def is_available(self) -> bool:
        """Check if the vision model is loaded in Ollama."""
        loaded = ollama.list_models()
        return self.model in loaded

    # ----------------------------------------------------------------
    # Image encoding
    # ----------------------------------------------------------------

    def _encode_image(self, image_source: str) -> str:
        """Accept path, URL, or raw base64. Return base64 string."""
        if image_source.startswith("data:image"):
            return image_source.split(",", 1)[1]

        if image_source.startswith(("http://", "https://")):
            r = requests.get(image_source, timeout=15)
            r.raise_for_status()
            return base64.b64encode(r.content).decode()

        if not os.path.exists(image_source):
            raise FileNotFoundError(f"Image not found: {image_source}")

        with open(image_source, "rb") as f:
            return base64.b64encode(f.read()).decode()

    # ----------------------------------------------------------------
    # Core vision call
    # ----------------------------------------------------------------

    def _vision_generate(self, prompt: str, image_source: str) -> str:
        """Call Ollama /api/generate with an image attachment."""
        image_b64 = self._encode_image(image_source)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {"temperature": 0.3}
        }

        r = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=180
        )
        r.raise_for_status()
        return r.json().get("response", "").strip()

    # ----------------------------------------------------------------
    # Task-specific methods
    # ----------------------------------------------------------------

    def describe(self, image_source: str) -> str:
        return self._vision_generate(
            "Describe this image in detail. What do you see?",
            image_source
        )

    def medical_analysis(self, image_source: str, clinical_context: str = "") -> str:
        prompt = (
            "You are a medical imaging specialist. Analyze this medical image.\n"
            "Describe:\n"
            "1. Image type and quality\n"
            "2. Anatomical structures visible\n"
            "3. Any notable findings or abnormalities\n"
            "4. Clinical significance\n\n"
            "Format your response as a structured medical report."
        )
        if clinical_context:
            prompt += f"\n\nClinical context: {clinical_context}"
        return self._vision_generate(prompt, image_source)

    def extract_text(self, image_source: str) -> str:
        return self._vision_generate(
            "Extract and transcribe ALL text visible in this image. Output only the extracted text.",
            image_source
        )

    def analyze_screenshot(self, image_source: str) -> str:
        return self._vision_generate(
            "Analyze this screenshot. Describe: the application/interface shown, "
            "key UI elements, any data or information displayed, and what actions "
            "could be taken from this state.",
            image_source
        )

    # ----------------------------------------------------------------
    # Universal dispatcher
    # ----------------------------------------------------------------

    def dispatch(self, task: str, image_source: str, params: dict = None) -> str:
        params = params or {}

        if task == "describe":
            return self.describe(image_source)
        elif task == "medical_analysis":
            context = params.get("clinical_context", "")
            return self.medical_analysis(image_source, context)
        elif task == "ocr":
            return self.extract_text(image_source)
        elif task == "screenshot":
            return self.analyze_screenshot(image_source)
        else:
            return self.describe(image_source)


# Singleton instance
vision = VisionConnector()
