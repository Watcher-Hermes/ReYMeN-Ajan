# -*- coding: utf-8 -*-
"""
browser_mcp_tool.py — Playwright MCP tarayıcı otomasyon aracı.

Hermes Agent Playwright MCP browser tool karşılığı.
Tam tarayıcı otomasyonu: navigate, click, type, screenshot, snapshot.

Kurulum: pip install playwright && playwright install chromium

Kullanım:
    from reymen.arac.browser_mcp_tool import BrowserMCP
    browser = BrowserMCP()
    browser.navigate("https://example.com")
    snapshot = browser.snapshot()
    browser.click("Submit button")
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_OK = True
except ImportError:
    PLAYWRIGHT_OK = False


class BrowserMCP:
    """Playwright MCP tarayıcı otomasyon aracı."""

    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self._headless = headless
        self._browser_type = browser_type
        self._pw = None
        self._browser: Optional[Any] = None
        self._context: Optional[Any] = None
        self._page: Optional[Any] = None
        self._tabs: List[Any] = []
        self._network_requests: List[Dict] = []
        self._console_messages: List[Dict] = []
        self._screenshot_dir = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "reymen" / ".ReYMeN" / "screenshots"
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_browser(self) -> bool:
        """Tarayıcının açık olduğundan emin olur."""
        if not PLAYWRIGHT_OK:
            return False

        if self._pw is None:
            self._pw = sync_playwright().start()

        if self._browser is None:
            launcher = getattr(self._pw, self._browser_type)
            self._browser = launcher.launch(headless=self._headless)

        if self._context is None:
            self._context = self._browser.new_context(
                viewport={"width": 1920, "height": 1080},
                locale="tr-TR",
                timezone_id="Europe/Istanbul",
            )
            # Network ve console dinle
            self._context.on("request", self._on_request)
            self._context.on("response", self._on_response)

        if self._page is None:
            self._page = self._context.new_page()
            self._page.on("console", self._on_console)

        return True

    def _on_request(self, request):
        self._network_requests.append({
            "url": request.url,
            "method": request.method,
            "type": request.resource_type,
            "zaman": time.time(),
        })

    def _on_response(self, response):
        pass

    def _on_console(self, msg):
        self._console_messages.append({
            "type": msg.type,
            "text": msg.text,
            "zaman": time.time(),
        })

    # ── Temel Eylemler ───────────────────────────────────────────────────────

    def navigate(self, url: str, timeout: int = 30000) -> Dict:
        """URL'ye gider."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            self._page.goto(url, timeout=timeout, wait_until="domcontentloaded")
            return {"ok": True, "url": self._page.url, "title": self._page.title()}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def snapshot(self, target: Optional[str] = None, depth: Optional[int] = None) -> Dict:
        """Accessibility snapshot alır."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            # Accessibility tree
            snapshot = self._page.accessibility.snapshot()

            # Basit metin versiyonu
            text_content = self._page.inner_text("body")[:5000]

            return {
                "ok": True,
                "title": self._page.title(),
                "url": self._page.url,
                "text": text_content,
                "snapshot": snapshot,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def click(self, target: str, double_click: bool = False, button: str = "left") -> Dict:
        """Elemente tıklar."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            # Farklı seçici stratejileri dene
            selectors = [
                f"text={target}",
                f"[aria-label='{target}']",
                f"button:has-text('{target}')",
                f"a:has-text('{target}')",
                target,  # CSS selector olarak da dene
            ]

            for selector in selectors:
                try:
                    el = self._page.locator(selector).first
                    if el.is_visible(timeout=2000):
                        if double_click:
                            el.dblclick()
                        else:
                            el.click(button=button)
                        return {"ok": True, "clicked": target, "selector": selector}
                except Exception:
                    continue

            return {"ok": False, "error": f"Element bulunamadı: {target}"}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def type_text(self, target: str, text: str, submit: bool = False,
                  slowly: bool = False) -> Dict:
        """Elemente yazar."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            selectors = [
                f"input[placeholder*='{target}']",
                f"textarea[placeholder*='{target}']",
                f"[aria-label*='{target}']",
                f"#{target}",
                target,
            ]

            for selector in selectors:
                try:
                    el = self._page.locator(selector).first
                    if el.is_visible(timeout=2000):
                        el.click()
                        if slowly:
                            el.type(text, delay=50)
                        else:
                            el.fill(text)
                        if submit:
                            el.press("Enter")
                        return {"ok": True, "typed": text[:50], "selector": selector}
                except Exception:
                    continue

            return {"ok": False, "error": f"Input bulunamadı: {target}"}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def press_key(self, key: str) -> Dict:
        """Tuşa basar."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            self._page.keyboard.press(key)
            return {"ok": True, "key": key}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def screenshot(self, full_page: bool = False, target: Optional[str] = None) -> Dict:
        """Ekran görüntüsü alır."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            fname = f"screen_{int(time.time())}.png"
            path = self._screenshot_dir / fname

            if target:
                # Element screenshot
                el = self._page.locator(target).first
                el.screenshot(path=str(path))
            else:
                self._page.screenshot(path=str(path), full_page=full_page)

            return {"ok": True, "path": str(path), "size": path.stat().st_size}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def scroll(self, direction: str = "down", amount: int = 3) -> Dict:
        """Sayfayı kaydırır."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}

        try:
            delta = amount * 300
            if direction in ("down", "asagi"):
                self._page.mouse.wheel(0, delta)
            elif direction in ("up", "yukari"):
                self._page.mouse.wheel(0, -delta)
            return {"ok": True, "direction": direction, "amount": amount}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def back(self) -> Dict:
        """Geri gider."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}
        try:
            self._page.go_back()
            return {"ok": True, "url": self._page.url}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def evaluate(self, js_code: str) -> Dict:
        """JavaScript çalıştırır."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}
        try:
            result = self._page.evaluate(js_code)
            return {"ok": True, "result": str(result)[:5000]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_images(self) -> List[str]:
        """Sayfadaki tüm görsellerin URL'lerini döner."""
        if not self._ensure_browser():
            return []
        try:
            return self._page.eval_on_selector_all("img", "els => els.map(e => e.src)")
        except Exception:
            return []

    def get_console(self, level: str = "info") -> List[Dict]:
        """Console mesajlarını döner."""
        levels = {"debug": 0, "info": 1, "warning": 2, "error": 3}
        min_level = levels.get(level, 1)
        return [m for m in self._console_messages
                if levels.get(m["type"], 1) >= min_level]

    def get_network(self, filter_url: Optional[str] = None) -> List[Dict]:
        """Network isteklerini döner."""
        if filter_url:
            import re
            return [r for r in self._network_requests if re.search(filter_url, r["url"])]
        return self._network_requests[-50:]

    # ── Tab Yönetimi ─────────────────────────────────────────────────────────

    def new_tab(self, url: Optional[str] = None) -> Dict:
        """Yeni sekme açar."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}
        try:
            page = self._context.new_page()
            self._tabs.append(page)
            if url:
                page.goto(url, timeout=30000)
            return {"ok": True, "tab_count": len(self._tabs)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def switch_tab(self, index: int) -> Dict:
        """Sekme değiştirir."""
        if index < 0 or index >= len(self._tabs):
            return {"ok": False, "error": f"Geçersiz sekme indeksi: {index}"}
        self._page = self._tabs[index]
        return {"ok": True, "url": self._page.url, "title": self._page.title()}

    def close_tab(self, index: Optional[int] = None) -> Dict:
        """Sekmeyi kapatır."""
        if index is None:
            index = len(self._tabs) - 1
        if index < 0 or index >= len(self._tabs):
            return {"ok": False, "error": f"Geçersiz sekme indeksi: {index}"}
        try:
            self._tabs[index].close()
            self._tabs.pop(index)
            if self._tabs:
                self._page = self._tabs[-1]
            return {"ok": True, "remaining": len(self._tabs)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Dialog ───────────────────────────────────────────────────────────────

    def handle_dialog(self, accept: bool = True, text: Optional[str] = None) -> Dict:
        """Dialog kutusunu işler."""
        if not self._ensure_browser():
            return {"ok": False, "error": "Playwright kurulu değil."}
        try:
            # Dialog handler'ı kaydet
            def handler(dialog):
                if accept:
                    dialog.accept(text or "")
                else:
                    dialog.dismiss()

            self._page.on("dialog", handler)
            return {"ok": True, "action": "accepted" if accept else "dismissed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ── Yaşam Döngüsü ────────────────────────────────────────────────────────

    def close(self) -> Dict:
        """Tarayıcıyı kapatır."""
        try:
            if self._page:
                self._page.close()
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._pw:
                self._pw.stop()

            self._page = None
            self._context = None
            self._browser = None
            self._pw = None
            self._tabs = []

            return {"ok": True, "message": "Tarayıcı kapatıldı."}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

_browser = None

def _get_browser() -> BrowserMCP:
    global _browser
    if _browser is None:
        _browser = BrowserMCP()
    return _browser


def run(islem: str = "navigate", url: str = "", target: str = "",
        text: str = "", key: str = "", js_code: str = "",
        direction: str = "down", amount: int = 3,
        full_page: bool = False, double_click: bool = False,
        submit: bool = False, slowly: bool = False,
        level: str = "info", filter_url: str = "",
        index: int = 0, accept: bool = True) -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    islem: navigate/snapshot/click/type/press/screenshot/scroll/back/evaluate
           get_images/get_console/get_network/new_tab/switch_tab/close_tab
           handle_dialog/close
    """
    browser = _get_browser()

    if islem == "navigate":
        if not url:
            return "[Hata]: url parametresi gerekli."
        r = browser.navigate(url)
        return f"✅ {r.get('title', '')} — {r.get('url', '')}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "snapshot":
        r = browser.snapshot()
        if not r["ok"]:
            return f"[Hata]: {r['error']}"
        return f"📄 {r['title']} ({r['url']})\n\n{r['text'][:3000]}"

    elif islem == "click":
        if not target:
            return "[Hata]: target parametresi gerekli."
        r = browser.click(target, double_click=double_click)
        return f"✅ Tıklandı: {target}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "type":
        if not target or not text:
            return "[Hata]: target ve text gerekli."
        r = browser.type_text(target, text, submit=submit, slowly=slowly)
        return f"✅ Yazıldı: {text[:50]}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "press":
        if not key:
            return "[Hata]: key parametresi gerekli."
        r = browser.press_key(key)
        return f"✅ Tuş: {key}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "screenshot":
        r = browser.screenshot(full_page=full_page, target=target or None)
        return f"✅ Ekran görüntüsü: {r['path']}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "scroll":
        r = browser.scroll(direction, amount)
        return f"✅ Kaydırıldı: {direction} x{amount}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "back":
        r = browser.back()
        return f"✅ Geri: {r.get('url', '')}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "evaluate":
        if not js_code:
            return "[Hata]: js_code parametresi gerekli."
        r = browser.evaluate(js_code)
        return f"✅ Sonuç: {r['result']}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "get_images":
        images = browser.get_images()
        return f"📷 {len(images)} görsel:\n" + "\n".join(images[:20]) if images else "📷 Görsel bulunamadı."

    elif islem == "get_console":
        msgs = browser.get_console(level)
        if not msgs:
            return "📋 Console boş."
        return "📋 Console:\n" + "\n".join(f"[{m['type']}] {m['text'][:100]}" for m in msgs[-20:])

    elif islem == "get_network":
        reqs = browser.get_network(filter_url or None)
        if not reqs:
            return "🌐 Network boş."
        return f"🌐 {len(reqs)} istek:\n" + "\n".join(f"{r['method']} {r['url'][:80]}" for r in reqs[-20:])

    elif islem == "new_tab":
        r = browser.new_tab(url or None)
        return f"✅ Yeni sekme açıldı" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "switch_tab":
        r = browser.switch_tab(index)
        return f"✅ Sekme {index}: {r.get('title', '')}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "close_tab":
        r = browser.close_tab(index)
        return f"✅ Sekme kapatıldı" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "handle_dialog":
        r = browser.handle_dialog(accept=accept)
        return f"✅ Dialog: {'kabul' if accept else 'reddedildi'}" if r["ok"] else f"[Hata]: {r['error']}"

    elif islem == "close":
        r = browser.close()
        global _browser
        _browser = None
        return f"✅ Tarayıcı kapatıldı" if r["ok"] else f"[Hata]: {r['error']}"

    return f"[Hata]: Bilinmeyen islem: {islem}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python browser_mcp_tool.py <islem> [parametreler]")
        sys.exit(1)

    islem = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else ""
    print(run(islem=islem, url=url))
