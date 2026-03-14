# ============================================================
# playwright_scraper.py — Antigravity Multi-Agent System
# Dynamic web scraping using Playwright + Chromium
# ============================================================

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import paths  # noqa: E402

import logging
from urllib.parse import quote_plus

logger = logging.getLogger("antigravity.playwright")


def scrape_url(url: str, timeout: int = 15000) -> dict:
    """
    Scrape a URL using Playwright (Chromium, headless).
    Returns dict with title, text, links.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (compatible; AntigravityBot/1.0)"})

        try:
            page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            page.wait_for_timeout(2000)

            title = page.title()
            body_text = page.inner_text("body")
            links = page.eval_on_selector_all(
                "a[href]",
                "els => els.map(e => ({text: e.innerText.trim(), href: e.href})).filter(e => e.href.startsWith('http')).slice(0, 20)"
            )
            return {"title": title, "text": body_text[:5000], "links": links, "url": url}

        except Exception as e:
            logger.warning(f"Playwright scrape error for {url}: {e}")
            return {"title": "", "text": "", "links": [], "url": url, "error": str(e)}
        finally:
            browser.close()


def scrape_url_text(url: str) -> str:
    """Simplified text-only scraper with requests fallback."""
    try:
        result = scrape_url(url)
        text = result.get("text", "")
        title = result.get("title", "")
        if text:
            return f"# {title}\n\n{text}" if title else text
    except Exception as e:
        logger.warning(f"Playwright text scrape failed for {url}: {e}")

    # Fallback
    try:
        import requests
        from bs4 import BeautifulSoup
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for el in soup(["script", "style", "nav", "footer"]):
            el.decompose()
        return soup.get_text(separator=" ", strip=True)[:4000]
    except Exception as e2:
        logger.error(f"requests fallback also failed for {url}: {e2}")
        return ""


def search_and_scrape(query: str, n: int = 3) -> str:
    """DuckDuckGo search via Playwright, scrape top N results."""
    from playwright.sync_api import sync_playwright

    search_url = f"https://duckduckgo.com/?q={quote_plus(query)}&ia=web"
    results_text = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (compatible; AntigravityBot/1.0)"})

        try:
            page.goto(search_url, timeout=20000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            links = page.eval_on_selector_all(
                "a[href]",
                """els => els
                    .map(e => e.href)
                    .filter(h => h.startsWith('http') && !h.includes('duckduckgo') && !h.includes('duck.com'))
                    .slice(0, 5)"""
            )

            for link in links[:n]:
                try:
                    page.goto(link, timeout=15000, wait_until="domcontentloaded")
                    page.wait_for_timeout(1500)
                    text = page.inner_text("body")[:2000]
                    title = page.title()
                    if text:
                        results_text.append(f"### {title}\nURL: {link}\n{text}")
                except Exception as e:
                    logger.warning(f"Could not scrape {link}: {e}")

        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
        finally:
            browser.close()

    if results_text:
        return f"## Web Search: {query}\n\n" + "\n\n---\n\n".join(results_text)
    return f"No web results retrievable for: {query}"
