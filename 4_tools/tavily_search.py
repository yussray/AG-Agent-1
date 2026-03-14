# ============================================================
# tavily_search.py — Antigravity Multi-Agent System
# Internet search using Tavily API with Playwright fallback
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from config import TAVILY_API_KEY

logger = logging.getLogger("antigravity.tavily")


class TavilySearch:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or TAVILY_API_KEY

    def is_available(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, n: int = 3, search_depth: str = "basic") -> list[dict]:
        """
        Search the web using Tavily API.
        Returns list of {title, url, content} dicts.
        """
        if not self.api_key:
            raise RuntimeError("TAVILY_API_KEY not configured.")

        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.api_key)
            response = client.search(
                query=query,
                max_results=n,
                search_depth=search_depth
            )
            results = response.get("results", [])
            logger.info(f"Tavily: {len(results)} results for '{query}'")
            return results
        except Exception as e:
            logger.error(f"Tavily search failed: {e}")
            raise

    def search_markdown(self, query: str, n: int = 3) -> str:
        """Return search results as a formatted markdown string."""
        try:
            results = self.search(query, n=n)
            if not results:
                return f"No results found for: {query}"

            lines = [f"## Search results for: {query}\n"]
            for i, r in enumerate(results, 1):
                title = r.get("title", "No title")
                url = r.get("url", "")
                content = r.get("content", "")[:500]
                lines.append(f"### {i}. {title}")
                lines.append(f"URL: {url}")
                lines.append(f"{content}\n")
            return "\n".join(lines)
        except Exception as e:
            return f"Tavily search failed: {e}"


def search_and_scrape(query: str, n: int = 3, url: str = None) -> str:
    """
    Priority chain:
    1. Tavily API (keyword search)
    2. Playwright (direct URL or DuckDuckGo search)
    3. requests + BeautifulSoup
    """
    tavily = TavilySearch()

    # If a direct URL is given, try Playwright first
    if url:
        try:
            from playwright_scraper import scrape_url_text
            result = scrape_url_text(url)
            if result and len(result) > 100:
                logger.info(f"Playwright direct scrape success: {url}")
                return result
        except Exception as e:
            logger.warning(f"Playwright URL scrape failed: {e}")

        try:
            from web_scraper import scrape_url
            result = scrape_url(url)
            if result and len(result.get("text", "")) > 100:
                return result["text"]
        except Exception as e:
            logger.warning(f"requests URL scrape failed: {e}")

    # Tavily keyword search
    if tavily.is_available():
        try:
            result = tavily.search_markdown(query, n=n)
            if result and "No results" not in result:
                logger.info("Tavily search success")
                return result
        except Exception as e:
            logger.warning(f"Tavily fallback to Playwright: {e}")

    # Playwright DuckDuckGo search
    try:
        from playwright_scraper import search_and_scrape as pw_search
        result = pw_search(query, n=n)
        if result and len(result) > 100:
            logger.info("Playwright search success")
            return result
    except Exception as e:
        logger.warning(f"Playwright search failed, falling back to requests: {e}")

    # requests + BeautifulSoup fallback
    try:
        from web_scraper import search_and_scrape as bs_search
        return bs_search(query, n=n)
    except Exception as e:
        logger.error(f"All search methods failed: {e}")
        return f"Search failed for query: {query}. Error: {e}"


# Module-level convenience
tavily_search = TavilySearch()
