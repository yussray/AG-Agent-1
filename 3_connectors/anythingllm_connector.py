# ============================================================
# anythingllm_connector.py — Antigravity Multi-Agent System
# Client wrapper for the AnythingLLM REST API
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import requests
import logging
from config import ANYTHINGLLM_BASE_URL, ANYTHINGLLM_API_KEY

logger = logging.getLogger("antigravity.anythingllm")


class AnythingLLMConnector:
    """
    Wrapper around the AnythingLLM REST API.
    Provides workspace management and RAG query capabilities.
    """

    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = (base_url or ANYTHINGLLM_BASE_URL).rstrip("/")
        self.api_key = api_key or ANYTHINGLLM_API_KEY
        self._default_workspace: str | None = None

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def is_available(self) -> bool:
        """Check if AnythingLLM is reachable."""
        try:
            r = requests.get(
                f"{self.base_url}/api/v1/auth",
                headers=self._headers(),
                timeout=3
            )
            return r.status_code in (200, 403)
        except Exception:
            return False

    # ----------------------------------------------------------------
    # Workspace management
    # ----------------------------------------------------------------

    def list_workspaces(self) -> list[dict]:
        try:
            r = requests.get(
                f"{self.base_url}/api/v1/workspaces",
                headers=self._headers(),
                timeout=5
            )
            r.raise_for_status()
            return r.json().get("workspaces", [])
        except Exception as e:
            logger.error(f"list_workspaces: {e}")
            return []

    def get_workspace_names(self) -> list[str]:
        return [ws.get("name", "") for ws in self.list_workspaces()]

    def get_default_workspace(self) -> str | None:
        if self._default_workspace:
            return self._default_workspace
        workspaces = self.list_workspaces()
        if workspaces:
            self._default_workspace = workspaces[0].get("slug")
        return self._default_workspace

    # ----------------------------------------------------------------
    # Chat / Query
    # ----------------------------------------------------------------

    def query_workspace(self, query: str, workspace_slug: str = None) -> str:
        slug = workspace_slug or self.get_default_workspace()
        if not slug:
            return "No workspace available in AnythingLLM."

        payload = {
            "message": query,
            "mode": "query"
        }

        try:
            r = requests.post(
                f"{self.base_url}/api/v1/workspace/{slug}/chat",
                json=payload,
                headers=self._headers(),
                timeout=60
            )
            r.raise_for_status()
            data = r.json()
            return (
                data.get("textResponse")
                or data.get("response")
                or data.get("message")
                or "[No response from AnythingLLM]"
            )
        except Exception as e:
            logger.error(f"query_workspace: {e}")
            raise

    def smart_query(self, query: str) -> str:
        """Query AnythingLLM — uses default workspace automatically."""
        return self.query_workspace(query)

    # ----------------------------------------------------------------
    # Document management
    # ----------------------------------------------------------------

    def list_documents(self, workspace_slug: str = None) -> list[dict]:
        slug = workspace_slug or self.get_default_workspace()
        if not slug:
            return []
        try:
            r = requests.get(
                f"{self.base_url}/api/v1/workspace/{slug}",
                headers=self._headers(),
                timeout=5
            )
            r.raise_for_status()
            ws = r.json().get("workspace", {})
            return ws.get("documents", [])
        except Exception as e:
            logger.error(f"list_documents: {e}")
            return []


# Singleton instance
anythingllm = AnythingLLMConnector()
