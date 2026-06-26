# -*- coding: utf-8 -*-
"""
web_search_tool.py — Web arama aracı.
Hermes Agent'in web_tools.py'sini kullanır.
ReYMeN tool registry'sine uyumlu wrapper.
"""
import sys
from pathlib import Path

# Hermes web_tools yolunu ekle
_HERMES_TOOLS = Path.home() / "AppData" / "Local" / "hermes" / "hermes-agent" / "tools"
if _HERMES_TOOLS.exists():
    _HERMES_TOOLS = str(_HERMES_TOOLS)
    if _HERMES_TOOLS not in sys.path:
        sys.path.insert(0, _HERMES_TOOLS)

try:
    from web_tools import web_search_tool as _hermes_search
    _HERMES_WEB = True
except ImportError:
    _HERMES_WEB = False


def web_search_ve_ozetle(sorgu: str, limit: int = 3) -> str:
    """Web araması yap ve sonucu özetle.

    Hermes Agent'in web_search_tool'unu kullanır.
    Hermes yoksa fallback olarak basit DuckDuckGo kullanır.

    Args:
        sorgu: Arama sorgusu
        limit: Max sonuç sayısı

    Returns:
        Özetlenmiş arama sonucu metni
    """
    if _HERMES_WEB:
        try:
            sonuc = _hermes_search(sorgu, limit=limit)
            if isinstance(sonuc, dict):
                data = sonuc.get("data", {})
                web_results = data.get("web", [])
                if web_results:
                    lines = []
                    for r in web_results[:limit]:
                        title = r.get("title", "")
                        desc = r.get("description", "")
                        url = r.get("url", "")
                        lines.append(f"• {title}: {desc}")
                    return "\n".join(lines) if lines else "Sonuç bulunamadı."
                return "Sonuç bulunamadı."
            return str(sonuc)
        except Exception as e:
            return f"Hata: {e}"

    # Fallback: DuckDuckGo
    try:
        import urllib.request
        import urllib.parse
        url = "https://html.duckduckgo.com/html/"
        data = urllib.parse.urlencode({"q": sorgu}).encode()
        req = urllib.request.Request(
            url, data=data,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        import re
        results = re.findall(
            r'<a[^>]*class="result__a"[^>]*>(.*?)</a>',
            html, re.DOTALL
        )
        if results:
            return "\n".join(
                f"• {re.sub(r'<[^>]+>', '', r).strip()}"
                for r in results[:limit]
            )
        return "Sonuç bulunamadı."
    except Exception as e:
        return f"Arama hatası: {e}"
