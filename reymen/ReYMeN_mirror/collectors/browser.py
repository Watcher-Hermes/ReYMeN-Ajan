"""
browser.py — JavaScript render gerektiren sayfalar icin Playwright tarayici.

Playwright Chromium'u headless acar, JS render eder,
sayfayi text olarak dondurur.
"""

import asyncio
from typing import Optional

from loguru import logger


class BrowserError(Exception):
    """Tarayici hatasi."""


class BrowserManager:
    """Playwright tarayici yoneticisi — singleton pattern."""

    _instance: Optional["BrowserManager"] = None
    _browser = None
    _context = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def start(self, headless: bool = True) -> None:
        """Tarayiciyi baslat."""
        if self._browser:
            return

        try:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            self._context = await self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36"
                ),
                ignore_https_errors=True,
            )
            logger.info("Playwright tarayici basladi")
        except ImportError:
            raise BrowserError("Playwright kurulu degil: pip install playwright && playwright install chromium")
        except Exception as e:
            raise BrowserError(f"Tarayici baslatilamadi: {e}")

    async def close(self) -> None:
        """Tarayiciyi kapat."""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None
        if hasattr(self, "_playwright") and self._playwright:
            await self._playwright.stop()
        logger.info("Playwright tarayici kapandi")

    async def render_page(self, url: str, timeout: float = 30.0) -> str:
        """
        URL'yi tarayicida ac, JS render et, text olarak al.

        Args:
            url: Hedef URL
            timeout: Maksimum bekleme (saniye)

        Returns:
            Sayfa text icerigi
        """
        await self.start()

        page = await self._context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=int(timeout * 1000))

            # Scroll ile dinamik icerik tetikle
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(0.5)

            text = await page.inner_text("body")
            baslik = await page.title()

            final = f"# {baslik}\n\n{text.strip()}" if baslik else text.strip()
            logger.info(f"render({url!r}): {len(final)} chars")
            return final
        except Exception as e:
            raise BrowserError(f"Sayfa render hatasi ({url}): {e}")
        finally:
            await page.close()


# Kucuk async fonksiyon
async def render_page(url: str, timeout: float = 30.0) -> str:
    """Kolay kullanim icin wrapper."""
    mgr = BrowserManager()
    return await mgr.render_page(url, timeout)
