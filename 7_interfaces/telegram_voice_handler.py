# ============================================================
# telegram_voice_handler.py — Antigravity Multi-Agent System
# Telegram voice message handler
# Downloads audio → faster-whisper → router pipeline
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
import tempfile

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from speech_to_text import stt

logger = logging.getLogger("antigravity.voice")


async def handle_voice_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    pipeline_fn
) -> None:
    """
    Handle a Telegram voice message end-to-end.
    Transcribes audio with Whisper and routes through the pipeline.
    """
    user = update.effective_user.first_name if update.effective_user else "User"

    if not stt.is_available():
        await update.message.reply_text(
            "⚠️ Speech-to-text not available.\n"
            "Install: `pip install faster-whisper`",
            parse_mode="Markdown"
        )
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    status_msg = await update.message.reply_text("🎤 Transcribing your voice message...")

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        await file.download_to_drive(tmp.name)
        audio_path = tmp.name

    try:
        logger.info(f"[{user}] Transcribing voice ({voice.duration}s)")
        result = stt.transcribe(audio_path)
        transcript = result["text"]
        lang = result.get("language", "?")

        if not transcript.strip():
            await status_msg.edit_text("⚠️ Could not transcribe the voice message. Please try again.")
            return

        await status_msg.edit_text(
            f"🎤 *Transcribed [{lang.upper()}]:*\n_{transcript}_",
            parse_mode="Markdown"
        )

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
        response = await pipeline_fn(transcript)

        if isinstance(response, dict):
            text = response.get("text", "")
            file_path = response.get("file")
            if text:
                await update.message.reply_text(_truncate(text))
            if file_path and os.path.exists(file_path):
                await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
                with open(file_path, "rb") as f:
                    await update.message.reply_document(
                        document=f,
                        filename=os.path.basename(file_path),
                        caption=f"📎 {os.path.basename(file_path)}"
                    )
        else:
            await update.message.reply_text(_truncate(str(response)))

    except Exception as e:
        logger.error(f"Voice handling error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Voice processing error: {e}")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


def _truncate(text: str, max_len: int = 4000) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 20] + "\n\n... *(truncated)*"
