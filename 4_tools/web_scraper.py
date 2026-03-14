# ============================================================
# web_scraper.py — Antigravity Multi-Agent System
# requests + BeautifulSoup fallback web scraper
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

logger = logging.getLogger("antigravity.web_scraper")

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AntigravityBot/1.0)"}


def scrape_url(url: str, timeout: int = 10) -> dict:
    """Scrape a URL and return title + plain text."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        for el in soup(["script", "style", "nav", "footer", "head"]):
            el.decompose()
        title = soup.title.string.strip() if soup.title else ""
        text = soup.get_text(separator=" ", strip=True)[:5000]
        return {"title": title, "text": text, "url": url}
    except Exception as e:
        logger.error(f"scrape_url failed for {url}: {e}")
        return {"title": "", "text": "", "url": url, "error": str(e)}


def scrape_url_smart(url: str) -> str:
    """Try Playwright first, fall back to requests."""
    try:
        from playwright_scraper import scrape_url_text
        result = scrape_url_text(url)
        if result and len(result) > 100:
            return result
    except Exception:
        pass
    result = scrape_url(url)
    return result.get("text", "")


def search_and_scrape(query: str, n: int = 3) -> str:
    """DuckDuckGo search via requests, scrape top N results."""
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    urls = []

    try:
        r = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.select("a.result__a")[:n]:
            href = a.get("href", "")
            if href.startswith("http"):
                urls.append(href)
    except Exception as e:
        logger.error(f"DuckDuckGo search failed: {e}")
        return f"Search failed: {e}"

    if not urls:
        return f"No search results found for: {query}"

    parts = [f"## Search results for: {query}\n"]
    for url in urls:
        result = scrape_url(url)
        if result.get("text"):
            parts.append(f"### {result['title']}\nURL: {url}\n{result['text'][:1500]}\n")

    return "\n\n".join(parts) if len(parts) > 1 else f"No content retrieved for: {query}"
