# ============================================================
# Dockerfile — Antigravity Multi-Agent System
# Runs the Telegram bot as a containerised background service
# ============================================================

FROM python:3.11-slim

# --- System dependencies ---
# ffmpeg: audio processing for Whisper
# Playwright Chromium system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxext6 \
    ca-certificates \
    fonts-liberation \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY 1_config/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's Chromium browser binary
RUN playwright install chromium

COPY . .

# Create outputs directory
RUN mkdir -p /app/8_outputs

# Default entrypoint: run the Telegram bot
CMD ["python", "-u", "7_interfaces/telegram_bot.py"]
