"""
web_search.py — Arama Katmani.

curl_cffi ile TLS fingerprint taklit ederek DuckDuckGo'da
bot engeli olmadan arama yapar.
"""

import asyncio
import random
from typing import Optional

from curl_cffi.requests import AsyncSession
from loguru import logger

# Gercek browser User-Agent listesi (rotasyon icin)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


def get_headers() -> dict:
    """Gercekci browser headers (rotasyonlu User-Agent)."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


async def human_delay(min_sec: float = 1.5, max_sec: float = 4.0) -> None:
    """Insan gibi rastgele bekleme."""
    await asyncio.sleep(random.uniform(min_sec, max_sec))


async def search(
    query: str,
    session=None,
    max_results: int = 10,
) -> list[dict]:
    """
    DuckDuckGo uzerinden arama yapar (API key gerektirmez).

    Bot engelini asmak icin:
    - curl_cffi + TLS impersonation
    - Session warming (cookie al)
    - Human delay

    Args:
        query: Arama sorgusu
        session: Kullanilmaz (curl_cffi kendi session yonetir)
        max_results: Max sonuc sayisi

    Returns:
        [{"title", "url", "snippet"}, ...]
    """
    results = []

    async with AsyncSession(impersonate="chrome120") as s:
        try:
            # Session warming — once ana sayfaya git (cookie al)
            await s.get(
                "https://duckduckgo.com",
                headers=get_headers(),
                timeout=10,
            )
            await human_delay(1.0, 2.5)

            # Arama istegi
            params = {
                "q": query,
                "kl": "us-en",   # Dil
                "kp": "-1",       # SafeSearch kapali
                "k1": "-1",       # Reklam yok
            }

            resp = await s.get(
                "https://html.duckduckgo.com/html/",
                params=params,
                headers=get_headers(),
                timeout=15,
            )

            if resp.status_code == 200:
                results = _parse_ddg_results(resp.text, max_results)
                logger.info(f"Arama tamamlandi: '{query}' -> {len(results)} sonuc")
            else:
                logger.warning(f"HTTP {resp.status_code}: {query}")

        except Exception as e:
            logger.error(f"Arama hatasi: {query} -> {e}")

    return results


def _parse_ddg_results(html: str, max_results: int) -> list[dict]:
    """DuckDuckGo HTML sonuclarini parse et."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    results = []

    for result in soup.select(".result")[:max_results]:
        title_el = result.select_one(".result__title")
        url_el = result.select_one(".result__url")
        snippet_el = result.select_one(".result__snippet")

        if title_el and url_el:
            results.append({
                "title": title_el.get_text(strip=True),
                "url": url_el.get_text(strip=True),
                "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
            })

    return results
