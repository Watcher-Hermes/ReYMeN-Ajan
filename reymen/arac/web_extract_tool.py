# -*- coding: utf-8 -*-
"""
web_extract_tool.py — URL'den markdown content extraction.

Hermes Agent web_extract_tool karşılığı.
Birden fazla URL'yi paralel çeker, markdown'a çevirir.
PDF URL'leri destekler. 5000+ char sayfaları özetler.

Kurulum: pip install beautifulsoup4 readability-lxml lxml
    (opsiyonel: pip install markdownify pdfminer.six)

Kullanım:
    from reymen.arac.web_extract_tool import web_extract
    sonuc = web_extract(["https://example.com", "https://other.com"])
"""

import html
import re
import urllib.request
import urllib.error
import concurrent.futures
from typing import List, Dict, Optional

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36"

# ── Yardımcılar ──────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int = 30) -> bytes:
    """URL'yi GET ile çeker, ham byte döner."""
    req = urllib.request.Request(url, headers={"User-Agent": _UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _html_to_markdown(html_content: str) -> str:
    """HTML'i temiz markdown'a çevirir."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")

        # Script/style/tag temizle
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        # Başlık
        title = soup.title.string.strip() if soup.title and soup.title.string else ""

        # readability varsa dene
        try:
            from readability import Document
            doc = Document(html_content)
            summary_html = doc.summary()
            soup2 = BeautifulSoup(summary_html, "lxml")
            text = soup2.get_text(separator="\n", strip=True)
        except Exception:
            text = soup.get_text(separator="\n", strip=True)

        # Temizle
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        result = "\n".join(lines)

        if title:
            result = f"# {title}\n\n{result}"

        return result[:10000]  # Max 10K char

    except ImportError:
        # Fallback: basit regex temizleme
        text = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.S | re.I)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(text)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        return "\n".join(lines)[:10000]


def _pdf_to_text(data: bytes) -> str:
    """PDF byte'larını metne çevirir."""
    try:
        from pdfminer.high_level import extract_text
        import io
        return extract_text(io.BytesIO(data))[:10000]
    except ImportError:
        # Fallback: pdfminer yoksa ham text ara
        text = data.decode("latin-1", errors="ignore")
        # PDF stream'lerinden text çıkar
        matches = re.findall(r'\(([^)]+)\)', text)
        return "\n".join(m for m in matches if len(m) > 3)[:5000]
    except Exception as e:
        return f"[PDF Hatası]: {e}"


def _extract_single(url: str, timeout: int = 30) -> Dict:
    """Tek URL'yi çeker ve markdown'a çevirir."""
    try:
        raw = _http_get(url, timeout=timeout)
        content_type = ""

        # PDF kontrolü
        if url.lower().endswith(".pdf") or b"%PDF" in raw[:10]:
            text = _pdf_to_text(raw)
            return {"url": url, "title": "PDF", "content": text, "error": None}

        # HTML → Markdown
        try:
            charset = "utf-8"
            if b"charset=" in raw[:2000]:
                m = re.search(rb'charset=["\']?([^"\'\s;]+)', raw[:2000])
                if m:
                    charset = m.group(1).decode("ascii", errors="ignore")

            html_str = raw.decode(charset, errors="replace")
        except Exception:
            html_str = raw.decode("utf-8", errors="replace")

        md = _html_to_markdown(html_str)

        # Başlık çıkar
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_str, re.I | re.S)
        title = html.unescape(title_match.group(1)).strip() if title_match else url

        return {"url": url, "title": title, "content": md, "error": None}

    except Exception as e:
        return {"url": url, "title": "", "content": "", "error": str(e)}


# ── Ana Fonksiyon ────────────────────────────────────────────────────────────

def web_extract(urls: List[str], timeout: int = 30, max_workers: int = 5) -> Dict:
    """
    Birden fazla URL'yi paralel çeker, markdown'a çevirir.

    Args:
        urls: Çekilecek URL listesi (max 5)
        timeout: Her URL için saniye cinsinden zaman aşımı
        max_workers: Paralel thread sayısı

    Returns:
        {"results": [{"url", "title", "content", "error"}, ...]}
    """
    urls = urls[:5]  # Max 5 URL

    if not urls:
        return {"results": [], "error": "URL listesi boş."}

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {executor.submit(_extract_single, url, timeout): url for url in urls}
        for future in concurrent.futures.as_completed(future_map):
            results.append(future.result())

    # Orijinal sırayı koru
    url_order = {url: i for i, url in enumerate(urls)}
    results.sort(key=lambda r: url_order.get(r["url"], 999))

    return {"results": results}


def run(urls: str = "", timeout: int = 30) -> str:
    """
    Motor entegrasyonu için run fonksiyonu.

    Args:
        urls: Virgülle ayrılmış URL listesi veya tek URL
        timeout: Zaman aşımı (saniye)

    Returns:
        Formatlı markdown sonuç
    """
    if not urls or not urls.strip():
        return "[Hata]: urls parametresi boş olamaz."

    # URL listesini parse et
    url_list = [u.strip() for u in urls.split(",") if u.strip()]
    if not url_list:
        url_list = [urls.strip()]

    sonuc = web_extract(url_list, timeout=timeout)

    if not sonuc.get("results"):
        return "[Hata]: Sonuç alınamadı."

    # Formatlı çıktı
    ciktilar = []
    for r in sonuc["results"]:
        if r.get("error"):
            ciktilar.append(f"## {r['url']}\n**Hata:** {r['error']}\n")
        else:
            baslik = r.get("title", r["url"])
            icerik = r.get("content", "")
            # Uzun içeriği kısalt
            if len(icerik) > 5000:
                icerik = icerik[:5000] + f"\n\n... ({len(r['content'])} karakter, kısaltıldı)"
            ciktilar.append(f"## {baslik}\n**Kaynak:** {r['url']}\n\n{icerik}\n")

    return "\n---\n\n".join(ciktilar)


# ── Doğrudan Çalıştırma ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python web_extract_tool.py <url1> [url2] [url3] ...")
        sys.exit(1)

    urls = sys.argv[1:]
    sonuc = web_extract(urls)
    for r in sonuc["results"]:
        if r.get("error"):
            print(f"[Hata] {r['url']}: {r['error']}")
        else:
            print(f"=== {r.get('title', r['url'])} ===")
            print(f"URL: {r['url']}")
            print(f"İçerik ({len(r['content'])} karakter):")
            print(r["content"][:2000])
            print()
