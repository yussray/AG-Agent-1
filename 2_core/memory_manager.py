# ============================================================
# memory_manager.py — Antigravity Multi-Agent System
# Per-user short-term conversation memory (in-memory, sliding window)
# ============================================================

import asyncio
import logging
from collections import defaultdict
from typing import List, Dict

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

from config import MEMORY_WINDOW_SIZE

logger = logging.getLogger("antigravity.memory")


class MemoryManager:
    """
    Manages per-user conversation history for short-term memory.

    - Keyed by Telegram user_id (int)
    - Each entry stores a list of {"role": "user"|"assistant", "content": "..."}
    - Sliding window: keeps at most MEMORY_WINDOW_SIZE messages (not turns)
    - Thread-safe via asyncio.Lock per user
    """

    def __init__(self, window_size: int = MEMORY_WINDOW_SIZE):
        self.window_size = window_size
        self._histories: Dict[int, List[dict]] = defaultdict(list)
        self._locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        logger.info(f"MemoryManager initialised — window={window_size} messages")

    def _lock(self, user_id: int) -> asyncio.Lock:
        return self._locks[user_id]

    async def get(self, user_id: int) -> List[dict]:
        """Return a copy of the user's conversation history."""
        async with self._lock(user_id):
            return list(self._histories[user_id])

    async def append_user(self, user_id: int, content: str) -> None:
        """Append a user turn to history."""
        async with self._lock(user_id):
            self._histories[user_id].append({"role": "user", "content": content})
            self._trim(user_id)

    async def append_assistant(self, user_id: int, content: str) -> None:
        """Append an assistant turn to history."""
        async with self._lock(user_id):
            self._histories[user_id].append({"role": "assistant", "content": content})
            self._trim(user_id)

    async def append_pair(self, user_id: int, user_content: str, assistant_content: str) -> None:
        """Append a full user+assistant exchange atomically."""
        async with self._lock(user_id):
            self._histories[user_id].append({"role": "user", "content": user_content})
            self._histories[user_id].append({"role": "assistant", "content": assistant_content})
            self._trim(user_id)

    async def clear(self, user_id: int) -> None:
        """Wipe the conversation history for a user."""
        async with self._lock(user_id):
            self._histories[user_id] = []
            logger.info(f"Memory cleared for user_id={user_id}")

    def _trim(self, user_id: int) -> None:
        """Trim history to window_size (called while lock is held)."""
        history = self._histories[user_id]
        if len(history) > self.window_size:
            # Drop oldest messages, always keep pairs intact (drop 2 at a time)
            excess = len(history) - self.window_size
            self._histories[user_id] = history[excess:]

    async def size(self, user_id: int) -> int:
        """Return number of messages stored for a user."""
        async with self._lock(user_id):
            return len(self._histories[user_id])

    def all_users(self) -> List[int]:
        """Return list of all user IDs with stored history."""
        return list(self._histories.keys())


# Singleton — import and use directly
memory = MemoryManager()
