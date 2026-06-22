"""
web_extract.py — Icerik Cekme Katmani.

Once curl_cffi ile dener (hizli, TLS fingerprint taklit).
Basarisiz olursa Playwright'a duser (JS render + bot evasion).
"""

import asyncio
import random
from typing import Optional

from loguru import logger
import trafilatura

# Hangi siteler JS render gerektirir
JS_REQUIRED_DOMAINS = [
    "twitter.com", "x.com", "instagram.com",
    "linkedin.com", "facebook.com",
    "bloomberg.com", "ft.com",
]


def needs_browser(url: str) -> bool:
    """URL'nin browser gerektirip gerektirmedigini kontrol et."""
    return any(domain in url for domain in JS_REQUIRED_DOMAINS)


async def extract(url: str, session=None) -> Optional[dict]:
    """
    URL'den icerik ceker.

    - Once curl_cffi ile dener (hizli, hafif)
    - Basarisiz olursa Playwright'a duser (JS render)
    """
    if needs_browser(url):
        return await _extract_with_browser(url)
    else:
        return await _extract_with_curl(url)


async def _extract_with_curl(url: str) -> Optional[dict]:
    """
    curl_cffi ile hizli cekme.
    TLS fingerprint Chrome'u taklit eder -> Cloudflare basic'i gecer.
    """
    from curl_cffi.requests import AsyncSession

    async with AsyncSession(impersonate="chrome120") as s:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
                "Referer": "https://www.google.com/",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            }

            # Insan gibi rastgele gecikme
            await asyncio.sleep(random.uniform(0.5, 2.0))

            resp = await s.get(url, headers=headers, timeout=20)

            if resp.status_code == 200:
                # trafilatura ile temiz metin cikar
                text = trafilatura.extract(
                    resp.text,
                    include_links=False,
                    include_images=False,
                    no_fallback=False,
                )

                if text and len(text) > 200:
                    return {
                        "url": url,
                        "content": text,
                        "method": "curl",
                        "length": len(text),
                    }

            logger.warning(f"curl basarisiz ({resp.status_code}), browser'a geciliyor: {url}")
            return await _extract_with_browser(url)

        except Exception as e:
            logger.error(f"curl extract hatasi: {url} -> {e}")
            return None


async def _extract_with_browser(url: str) -> Optional[dict]:
    """
    Playwright ile tam browser render.

    Bot tespitini gecmek icin:
    - webdriver flag gizlenir
    - Insan gibi scroll yapilir
    - Rastgele mouse hareketi simule edilir
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-infobars",
                "--window-size=1920,1080",
                "--disable-extensions",
            ],
        )

        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            java_script_enabled=True,
            accept_downloads=False,
        )

        # webdriver tespitini engelle
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Insan gibi scroll (bot tespitini gecmek icin davranissal)
            await _human_scroll(page)

            html = await page.content()
            text = trafilatura.extract(html, include_links=False)

            if text and len(text) > 200:
                return {
                    "url": url,
                    "content": text,
                    "method": "browser",
                    "length": len(text),
                }

        except Exception as e:
            logger.error(f"Browser extract hatasi: {url} -> {e}")
        finally:
            await browser.close()

    return None


async def _human_scroll(page) -> None:
    """Insan gibi yavas scroll — davranissal bot tespitini gecer."""
    for _ in range(random.randint(3, 6)):
        scroll_amount = random.randint(200, 600)
        await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        await asyncio.sleep(random.uniform(0.3, 1.2))
