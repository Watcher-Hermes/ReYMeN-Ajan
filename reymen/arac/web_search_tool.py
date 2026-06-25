# -*- coding: utf-8 -*-
"""
web_search_tool.py — Otomatik web arama aracı.

ReYMeN sorulan soruyu hafızada bulamazsa otomatik web araması yapar.
DuckDuckGo, Brave, SearXNG destekler.

Kullanım:
    from reymen.arac.web_search_tool import web_search
    sonuc = web_search("altın ons fiyatı bugün")
"""

import html
import json
import os
import re
import urllib.parse
import urllib.request
from typing import List, Dict, Optional

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0"
_HEADERS = {"User-Agent": _UA}


def _http_get(url: str, params: dict = None, timeout: int = 15) -> str:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _temizle(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


# ── DuckDuckGo HTML ──────────────────────────────────────────────────────────

def _ddg_ara(sorgu: str, limit: int = 5) -> List[Dict]:
    """DuckDuckGo HTML araması."""
    try:
        url = "https://html.duckduckgo.com/html/"
        data = urllib.parse.urlencode({"q": sorgu}).encode()
        req = urllib.request.Request(url, data=data, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_text = resp.read().decode("utf-8", errors="replace")

        sonuclar = []
        # Result blocks
        blocks = re.findall(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>',
            html_text, re.S
        )

        for url, baslik, aciklama in blocks[:limit]:
            url = html.unescape(url)
            # DDG redirect URL'ini temizle
            if "uddg=" in url:
                match = re.search(r'uddg=([^&]+)', url)
                if match:
                    url = urllib.parse.unquote(match.group(1))

            sonuclar.append({
                "baslik": _temizle(baslik),
                "url": url,
                "aciklama": _temizle(aciklama),
            })

        return sonuclar

    except Exception as e:
        return [{"hata": f"DDG arama hatası: {e}"}]


# ── DuckDuckGo Lite ──────────────────────────────────────────────────────────

def _ddg_lite_ara(sorgu: str, limit: int = 5) -> List[Dict]:
    """DuckDuckGo Lite araması (fallback)."""
    try:
        url = "https://lite.duckduckgo.com/lite/"
        data = urllib.parse.urlencode({"q": sorgu}).encode()
        req = urllib.request.Request(url, data=data, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html_text = resp.read().decode("utf-8", errors="replace")

        sonuclar = []
        links = re.findall(
            r'<a[^>]+rel="nofollow"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            html_text, re.S
        )

        for url, baslik in links[:limit]:
            if url.startswith("http"):
                sonuclar.append({
                    "baslik": _temizle(baslik),
                    "url": url,
                    "aciklama": "",
                })

        return sonuclar

    except Exception as e:
        return [{"hata": f"DDG Lite arama hatası: {e}"}]


# ── Brave Search (API key varsa) ─────────────────────────────────────────────

def _brave_ara(sorgu: str, limit: int = 5) -> List[Dict]:
    """Brave Search API."""
    api_key = os.getenv("BRAVE_API_KEY", "")
    if not api_key:
        return []

    try:
        url = "https://api.search.brave.com/res/v1/web/search"
        params = {"q": sorgu, "count": limit}
        full_url = url + "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(full_url, headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key,
        })

        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        sonuclar = []
        for r in data.get("web", {}).get("results", [])[:limit]:
            sonuclar.append({
                "baslik": r.get("title", ""),
                "url": r.get("url", ""),
                "aciklama": r.get("description", ""),
            })

        return sonuclar

    except Exception as e:
        return [{"hata": f"Brave arama hatası: {e}"}]


# ── SearXNG (varsa) ──────────────────────────────────────────────────────────

def _searxng_ara(sorgu: str, limit: int = 5) -> List[Dict]:
    """SearXNG instance araması."""
    searxng_url = os.getenv("SEARXNG_URL", "")
    if not searxng_url:
        return []

    try:
        params = {"q": sorgu, "format": "json", "pageno": 1}
        full_url = searxng_url + "?" + urllib.parse.urlencode(params)

        req = urllib.request.Request(full_url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        sonuclar = []
        for r in data.get("results", [])[:limit]:
            sonuclar.append({
                "baslik": r.get("title", ""),
                "url": r.get("url", ""),
                "aciklama": r.get("content", ""),
            })

        return sonuclar

    except Exception as e:
        return [{"hata": f"SearXNG arama hatası: {e}"}]


# ── Ana Fonksiyon ────────────────────────────────────────────────────────────

def web_search(sorgu: str, limit: int = 5, dil: str = "tr") -> Dict:
    """
    Web araması yapar (çok kaynaklı fallback).

    Args:
        sorgu: Arama sorgusu
        limit: Max sonuç sayısı
        dil: Arama dili (tr/en)

    Returns:
        {"results": [...], "kaynak": "...", "error": None}
    """
    if not sorgu or not sorgu.strip():
        return {"results": [], "kaynak": "", "error": "Sorgu boş olamaz."}

    # Dil eki
    if dil == "tr":
        sorgu = sorgu + " türkçe"
    elif dil == "en":
        sorgu = sorgu + " english"

    # Provider zinciri
    providers = [
        ("brave", _brave_ara),
        ("searxng", _searxng_ara),
        ("duckduckgo", _ddg_ara),
        ("duckduckgo_lite", _ddg_lite_ara),
    ]

    for kaynak, fonksiyon in providers:
        try:
            sonuclar = fonksiyon(sorgu, limit)
            if sonuclar and not any("hata" in s for s in sonuclar):
                return {
                    "results": sonuclar,
                    "kaynak": kaynak,
                    "error": None,
                }
        except Exception:
            continue

    return {"results": [], "kaynak": "", "error": "Hiçbir arama motoru çalışmadı."}


def web_search_ve_ozetle(sorgu: str, limit: int = 3) -> str:
    """
    Web araması yapar ve sonuçları özetler.
    Fiyat/kur sorgularında ilk sonucun sayfasından CANLI veri çeker.

    Args:
        sorgu: Arama sorgusu
        limit: Max sonuç

    Returns:
        Formatlı özet
    """
    sonuc = web_search(sorgu, limit=limit)

    if sonuc.get("error"):
        return f"[Arama Hatası]: {sonuc['error']}"

    if not sonuc["results"]:
        return f"'{sorgu}' için sonuç bulunamadı."

    satirlar = [f"🔍 '{sorgu}' arama sonuçları ({sonuc['kaynak']}):\n"]

    # ── Fiyat sorgularında ilk sonuçtan CANLI veri çek ──
    _fiyat_kelimeler = ["fiyat", "kur", "dolar", "euro", "altın", "altin",
                        "bitcoin", "borsa", "ne kadar", "kaç tl"]
    _fiyat_sorgu = any(k in sorgu.lower() for k in _fiyat_kelimeler)

    _canli_veri = ""
    if _fiyat_sorgu and sonuc["results"]:
        ilk_url = sonuc["results"][0].get("url", "")
        if ilk_url and ilk_url.startswith("http"):
            try:
                _canli_veri = _sayfadan_fiyat_cek(ilk_url, sorgu)
            except Exception:
                pass

    if _canli_veri:
        satirlar.append(f"📊 **CANLI VERİ (sayfadan çekildi):**\n{_canli_veri}\n")

    for i, r in enumerate(sonuc["results"], 1):
        baslik = r.get("baslik", "Başlık yok")
        url = r.get("url", "")
        aciklama = r.get("aciklama", "")

        satirlar.append(f"{i}. **{baslik}**")
        if aciklama:
            satirlar.append(f"   {aciklama[:200]}")
        if url:
            satirlar.append(f"   🔗 {url}")
        satirlar.append("")

    return "\n".join(satirlar)


def _sayfadan_fiyat_cek(url: str, sorgu: str) -> str:
    """
    Verilen URL'den fiyat/kur bilgisini çeker.
    Bigpara, altin.in, doviz.com gibi sitelerden canlı veri extract eder.
    """
    try:
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html_content = resp.read().decode("utf-8", errors="replace")

        # TL formatı: 3.993,19 veya 3,993.19
        tl_fiyatlar = re.findall(r'(\d{1,3}[.,]\d{3}[.,]\d{2})\s*(?:TL|₺)', html_content)

        # USD formatı: $3,993.19 veya 3.993,19 USD
        usd_fiyatlar = re.findall(r'(?:\$|USD)\s*(\d{1,4}[.,]\d{2,4})', html_content)
        usd_fiyatlar2 = re.findall(r'(\d{1,4}[.,]\d{2,4})\s*(?:USD|\$)', html_content)

        # ONS fiyatı (genellikle sayfada büyük fontla gösterilir)
        ons_fiyat = re.findall(r'(\d{1,4}[.,]\d{2})\s*(?:USD|\$)', html_content)

        sonuc_parcalari = []

        if tl_fiyatlar:
            # En büyük TL fiyatı genellikle ana fiyat
            en_buyuk = max(tl_fiyatlar, key=lambda x: float(x.replace('.', '').replace(',', '.')))
            sonuc_parcalari.append(f"TL: {en_buyuk}")

        if usd_fiyatlar:
            sonuc_parcalari.append(f"USD: {usd_fiyatlar[0]}")
        elif usd_fiyatlar2:
            sonuc_parcalari.append(f"USD: {usd_fiyatlar2[0]}")

        # Gram altın
        gram = re.findall(r'gram[:\s]*(\d{1,2}[.,]\d{3}[.,]\d{2})', html_content, re.IGNORECASE)
        if gram:
            sonuc_parcalari.append(f"Gram: {gram[0]} TL")

        if sonuc_parcalari:
            return " | ".join(sonuc_parcalari)

        return ""

    except Exception as e:
        return ""


# ── Motor Entegrasyonu ───────────────────────────────────────────────────────

def run(sorgu: str = "", limit: int = 5, dil: str = "tr",
        ozetle: str = "true") -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    Args:
        sorgu: Arama sorgusu
        limit: Max sonuç
        dil: Arama dili
        ozetle: Sonuçları özetle (true/false)
    """
    if not sorgu or not sorgu.strip():
        return "[Hata]: sorgu parametresi boş olamaz."

    if ozetle.lower() in ("true", "1", "evet"):
        return web_search_ve_ozetle(sorgu.strip(), limit=limit)

    sonuc = web_search(sorgu.strip(), limit=limit, dil=dil)

    if sonuc.get("error"):
        return f"[Hata]: {sonuc['error']}"

    if not sonuc["results"]:
        return f"'{sorgu}' için sonuç bulunamadı."

    # JSON formatında döner
    return json.dumps(sonuc, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python web_search_tool.py <sorgu>")
        sys.exit(1)

    sorgu = " ".join(sys.argv[1:])
    print(web_search_ve_ozetle(sorgu))
