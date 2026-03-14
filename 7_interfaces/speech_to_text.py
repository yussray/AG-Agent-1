# ============================================================
# speech_to_text.py — Antigravity Multi-Agent System
# Speech transcription engine using faster-whisper
# Converts audio files to text locally (GPU accelerated)
# ============================================================

import os
import logging

logger = logging.getLogger("antigravity.speech")

WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")  # tiny/base/small/medium/large


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


WHISPER_DEVICE = "cuda" if _cuda_available() else "cpu"
WHISPER_COMPUTE = "float16" if WHISPER_DEVICE == "cuda" else "int8"


class SpeechToText:
    """
    Wrapper around faster-whisper for local speech transcription.
    Lazy-loads the model on first use to avoid startup delay.
    """

    def __init__(self, model_size: str = None, device: str = None, compute_type: str = None):
        self.model_size = model_size or WHISPER_MODEL_SIZE
        self.device = device or WHISPER_DEVICE
        self.compute_type = compute_type or WHISPER_COMPUTE
        self._model = None

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded.")
        return self._model

    def is_available(self) -> bool:
        try:
            import faster_whisper
            return True
        except ImportError:
            return False

    def transcribe(self, audio_path: str, language: str = None) -> dict:
        """
        Transcribe an audio file to text.

        Returns dict with: text, language, duration, segments
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        model = self._load_model()
        transcribe_kwargs = {"beam_size": 5}
        if language:
            transcribe_kwargs["language"] = language

        segments, info = model.transcribe(audio_path, **transcribe_kwargs)

        full_text = ""
        all_segments = []

        for seg in segments:
            full_text += seg.text + " "
            all_segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip()
            })

        result = {
            "text": full_text.strip(),
            "language": info.language,
            "language_probability": round(info.language_probability, 2),
            "duration": round(info.duration, 2),
            "segments": all_segments
        }

        logger.info(f"Transcribed {round(info.duration, 1)}s [{info.language}]: {full_text[:80]}...")
        return result

    def transcribe_text_only(self, audio_path: str, language: str = None) -> str:
        result = self.transcribe(audio_path, language)
        return result["text"]


# Singleton instance
stt = SpeechToText()
