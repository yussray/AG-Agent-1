# ============================================================
# telegram_bot.py — Antigravity Multi-Agent System
# Telegram interface — routes messages through the full pipeline
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import asyncio
import logging
import tempfile
from dotenv import load_dotenv

load_dotenv()

from telegram import Update, Message
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ContextTypes
)
from telegram.constants import ChatAction

from ollama_connector import ollama
from anythingllm_connector import anythingllm
from vision_connector import vision
from workflow_engine import engine
from research_workflow import (
    build_research_workflow, build_slides_workflow, build_qa_workflow,
    build_web_search_workflow
)
from router import route, describe_route, select_model
from config import REASONING_MODEL, VISION_MODEL, TELEGRAM_BOT_TOKEN, MEDICAL_MODEL
from speech_to_text import stt
from telegram_voice_handler import handle_voice_message

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("antigravity.telegram")


def startup_check() -> str:
    lines = ["🚀 *Antigravity AI Agent starting...*\n"]
    if ollama.is_available():
        lines.append("✅ Ollama online")
    else:
        lines.append("❌ Ollama offline — text tasks will fail")
    if anythingllm.is_available():
        ws = anythingllm.get_workspace_names()
        lines.append(f"✅ AnythingLLM online — workspaces: {', '.join(ws) if ws else 'none'}")
    else:
        lines.append("⚠️  AnythingLLM offline — RAG disabled")
    if vision.is_available():
        lines.append(f"✅ Vision model ready ({VISION_MODEL.split('/')[-1]})")
    else:
        lines.append("⚠️  Vision model not loaded")
    if stt.is_available():
        lines.append("✅ Speech-to-text ready (faster-whisper)")
    else:
        lines.append("⚠️  Speech-to-text not available")
    return "\n".join(lines)


async def run_pipeline(user_input: str, image_path: str = None) -> str:
    """Full Antigravity pipeline: route → dispatch → return response."""
    try:
        route_result = route(user_input)
        destination = route_result.get("route", "ollama")
        task = route_result.get("task", "general")
        params = route_result.get("parameters", {})

        logger.info(f"Route: {destination} | Task: {task}")

        if destination == "vision" or image_path:
            if not image_path:
                return "📷 Please send an image along with your request."
            if not vision.is_available():
                return f"⚠️ Vision model not loaded. Run: `ollama pull {VISION_MODEL}`"
            return vision.dispatch(task, image_path, params)

        elif destination == "anythingllm":
            if not anythingllm.api_key:
                return "⚠️ AnythingLLM API key not configured."
            query = params.get("query", user_input)
            result = engine.run("Q&A with RAG", steps=build_qa_workflow(query))
            return result.context.get("refine_answer", result.context.get("query_knowledge_base", "No answer found."))

        elif destination == "ollama":
            if task == "generate_slides":
                topic = params.get("topic", user_input)
                result = engine.run("Generate Slides", steps=build_slides_workflow(topic))
                slide_text = result.context.get("run_designer", result.context.get("slide_prompt", ""))
                if slide_text:
                    from make_slides import make_slides
                    import re
                    slug = re.sub(r'[^\w]', '_', topic.lower())[:25]
                    pptx_path = make_slides(slide_text, title=topic, filename=f"slides_{slug}.pptx")
                    return {"text": f"✅ Slides generated!\n\n{slide_text[:800]}...", "file": pptx_path}
                return slide_text

            elif task == "research_report":
                topic = params.get("topic", user_input)
                result = engine.run("Research Report", steps=build_research_workflow(topic))
                report_text = result.context.get("generate_summary", "")
                if report_text:
                    from make_pdf import make_pdf
                    import re
                    slug = re.sub(r'[^\w]', '_', topic.lower())[:25]
                    pdf_path = make_pdf(report_text, title=topic, filename=f"report_{slug}.pdf")
                    return {"text": f"📚 Research report generated!\n\n{report_text[:800]}...", "file": pdf_path}
                return report_text

            elif task == "web_search":
                query = params.get("query", user_input)
                url = params.get("url", None)
                result = engine.run("Web Search", steps=build_web_search_workflow(query=query, url=url))
                return result.context.get("summarise_results", result.context.get("scraped_content", "No results found."))

            else:
                model = select_model(route_result)
                return ollama.generate(model=model, prompt=user_input)

        else:
            model = select_model(route_result)
            return ollama.generate(model=model, prompt=user_input)

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return f"❌ Error: {e}"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = startup_check()
    await update.message.reply_text(
        f"{status}\n\n"
        "💬 *Ready! Send me any request.*\n\n"
        "Examples:\n"
        "• Create slides about bariatric surgery\n"
        "• Summarize my uploaded research\n"
        "• Send an image for analysis\n"
        "Commands: /start /status /workspaces /help",
        parse_mode="Markdown"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(startup_check(), parse_mode="Markdown")


async def cmd_workspaces(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        workspaces = anythingllm.list_workspaces()
        if not workspaces:
            await update.message.reply_text("📚 No workspaces found in AnythingLLM.")
            return
        lines = ["📚 *AnythingLLM Workspaces:*"]
        for ws in workspaces:
            lines.append(f"  • {ws.get('name')} (slug: `{ws.get('slug')}`)")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Could not fetch workspaces: {e}")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 *Antigravity AI Agent*\n\n"
        "*Text Commands:*\n"
        "• Ask any question\n"
        "• `Create slides about [topic]`\n"
        "• `Research [topic]`\n"
        "• `Summarize my documents about [topic]`\n"
        "• `Write code for [task]`\n\n"
        "*Image Commands:*\n"
        "• Send an image with caption: `Analyze this X-ray`\n\n"
        "*Voice Messages:*\n"
        "• Send a voice message — it will be transcribed and processed!\n\n"
        "*Bot Commands:*\n"
        "/start — startup status\n"
        "/status — system health\n"
        "/workspaces — list RAG workspaces\n"
        "/help — this message"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    user = update.effective_user.first_name
    logger.info(f"[{user}] Text: {user_input[:80]}")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    response = await run_pipeline(user_input)

    if isinstance(response, dict):
        text = response.get("text", "")
        file_path = response.get("file")
        if text:
            await update.message.reply_text(_truncate(text), parse_mode=None)
        if file_path and os.path.exists(file_path):
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
            with open(file_path, "rb") as f:
                await update.message.reply_document(document=f, filename=os.path.basename(file_path),
                                                     caption=f"📎 {os.path.basename(file_path)}")
    else:
        await update.message.reply_text(_truncate(str(response)))


async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or "Describe this image in detail."
    user = update.effective_user.first_name
    logger.info(f"[{user}] Image received. Caption: {caption[:60]}")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        await file.download_to_drive(tmp.name)
        image_path = tmp.name

    try:
        response = await run_pipeline(caption, image_path=image_path)
        if isinstance(response, dict):
            response = response.get("text", str(response))
        await update.message.reply_text(_truncate(str(response)))
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    caption = update.message.caption or "Analyze this image."
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text("📎 File received. Document processing available via the tool layer.")
        return
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    file = await context.bot.get_file(doc.file_id)
    ext = doc.mime_type.split("/")[-1]
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        await file.download_to_drive(tmp.name)
        image_path = tmp.name
    try:
        response = await run_pipeline(caption, image_path=image_path)
        if isinstance(response, dict):
            response = response.get("text", str(response))
        await update.message.reply_text(_truncate(str(response)))
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)


def _truncate(text: str, max_len: int = 4000) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 20] + "\n\n... *(truncated)*"


def main():
    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not set in .env file.")
        sys.exit(1)

    print(startup_check())
    print("\n📱 Starting Telegram bot...\n")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("workspaces", cmd_workspaces))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    async def _voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await handle_voice_message(update, context, pipeline_fn=run_pipeline)

    app.add_handler(MessageHandler(filters.VOICE, _voice_handler))

    print("✅ Bot is running. Press Ctrl+C to stop.\n")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
