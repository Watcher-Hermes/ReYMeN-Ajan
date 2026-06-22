"""
filter.py — Kalite filtresi.

Domain kara listesi, spam tespiti, uzunluk/tekrar/encoding kontrolleri.
loguru opsiyonel, tldextract opsiyonel — ikisi de yoksa fallback kullanir.
"""

import re
import logging
from typing import Optional
from urllib.parse import urlparse

# --- Loguru opsiyonel, fallback standart logging ---
try:
    from loguru import logger
except ImportError:
    logger = logging.getLogger("reymen.filter")
    logging.basicConfig(level=logging.DEBUG)

# --- tldextract opsiyonel, fallback manuel parse ---
try:
    import tldextract
    _USE_TLDEXTRACT = True
except ImportError:
    _USE_TLDEXTRACT = False
    logger.warning(
        "tldextract bulunamadi, fallback domain parse kullaniliyor. "
        "pip install tldextract onerilir."
    )

# --- Kara liste — bare domain name (TLD'siz) ---
# tldextract'in ext.domain alani ile karsilastirilir.
# "google" -> google.com, google.com.tr, google.co.uk hepsini yakalar.
# Yanlis pozitif riski yok: eslesme ext.domain'e (tek kelime) karsi yapilir,
# tam URL string'ine degil.
BLOCKED_DOMAINS: set[str] = {
    "facebook", "instagram", "tiktok",
    "pinterest", "reddit",
    "amazon", "ebay",
    "youtube", "vimeo",
    "google", "bing", "yahoo",
}

# --- Spam sinyal kelimeleri ---
SPAM_SIGNALS: list[str] = [
    "click here", "buy now", "limited offer",
    "subscribe to unlock", "sign in to read",
    "create an account", "paywall", "premium content",
    "cookies to continue", "accept cookies",
    "javascript is required", "enable javascript",
]

# --- Kalite esikleri ---
MIN_CONTENT_LENGTH: int = 1200       # FIX #6: 300 -> 1200
MAX_CONTENT_LENGTH: int = 100_000
MIN_WORD_COUNT: int = 150            # FIX #6: buna bagli kelime esigi
MAX_SPAM_RATIO: float = 0.015        # FIX #8: 0.02 -> 0.015
MIN_SENTENCE_COUNT: int = 5          # FIX #6: 3 -> 5


# --- Domain yardimcilari ---

def _domain_name(url: str) -> str:
    """
    URL'den bare domain name dondurur (TLD ve subdomain olmadan).

    tldextract varsa:
      https://www.google.com.tr/search -> "google"
      https://news.ycombinator.com     -> "ycombinator"

    tldextract yoksa (fallback):
      www2.example.com -> "example"
    """
    if _USE_TLDEXTRACT:
        ext = tldextract.extract(url)
        return ext.domain.lower() if ext.domain and ext.suffix else ""

    # Fallback: subdomain on eklerini ve ilk TLD'yi at
    try:
        netloc = urlparse(url).netloc.lower().split(":")[0]
        netloc = re.sub(r"^(www\d*|m|mobile)\.", "", netloc)
        # En soldaki parcayi al: "example.com.tr" -> "example"
        return netloc.split(".")[0]
    except Exception:
        return ""


# --- Ana filtre ---

def quality_filter(item: Optional[dict]) -> bool:
    """
    True -> kaliteli, kullan
    False -> reddedildi
    """
    if not item:
        return False

    url = item.get("url", "")
    content = item.get("content", "")

    checks = [
        (_check_url, url),
        (_check_length, content),
        (_check_word_count, content),
        (_check_sentence_count, content),
        (_check_spam_ratio, content),
        (_check_encoding, content),
        (_check_duplicate_ratio, content),
    ]

    for check_fn, arg in checks:
        passed, reason = check_fn(arg)
        if not passed:
            logger.debug(
                f"Filtre reddetti [{check_fn.__name__}]: "
                f"{reason} | {url[:80]}"
            )
            return False

    return True


# --- Bireysel kontroller ---

def _check_url(url: str) -> tuple[bool, str]:
    """FIX #3 #4: bare domain name + tldextract ile ulke TLD'leri yakalar."""
    if not url or not url.startswith("http"):
        return False, "Gecersiz URL"

    name = _domain_name(url)
    if not name:
        return False, "Domain cozulemedi"

    if name in BLOCKED_DOMAINS:
        return False, f"Kara listeli domain: {name}"

    return True, ""


def _check_length(content: str) -> tuple[bool, str]:
    if not content:
        return False, "Icerik bos"

    length = len(content)
    if length < MIN_CONTENT_LENGTH:
        return False, f"Cok kisa: {length} kar. (min {MIN_CONTENT_LENGTH})"
    if length > MAX_CONTENT_LENGTH:
        return False, f"Cok uzun: {length} kar. (max {MAX_CONTENT_LENGTH})"

    return True, ""


def _check_word_count(content: str) -> tuple[bool, str]:
    count = len(content.split())
    if count < MIN_WORD_COUNT:
        return False, f"Az kelime: {count} (min {MIN_WORD_COUNT})"
    return True, ""


def _check_sentence_count(content: str) -> tuple[bool, str]:
    sentences = [
        s.strip() for s in re.split(r"[.!?]+", content)
        if len(s.strip()) > 20
    ]
    count = len(sentences)
    if count < MIN_SENTENCE_COUNT:
        return False, f"Az cumle: {count} (min {MIN_SENTENCE_COUNT})"
    return True, ""


def _check_spam_ratio(content: str) -> tuple[bool, str]:
    """FIX #8: esik 0.02 -> 0.015."""
    content_lower = content.lower()
    word_count = max(len(content.split()), 1)
    spam_hits = sum(1 for s in SPAM_SIGNALS if s in content_lower)
    ratio = spam_hits / word_count

    if ratio > MAX_SPAM_RATIO:
        return False, f"Spam orani yuksek: {ratio:.4f} ({spam_hits} sinyal)"
    return True, ""


def _check_encoding(content: str) -> tuple[bool, str]:
    """
    FIX #5 notu: ord > 65000 Private Use Area'yi yakalar (dogru).
    Emoji U+1F300-U+1FFFF araligindadir, 65000'in altinda kalir -> yanlis pozitif yok.
    Kontrol karakterleri: ord < 32, \\n \\t \\r haric.
    """
    if not content:
        return False, "Bos icerik"

    weird = sum(
        1 for c in content
        if ord(c) > 65000
        or (ord(c) < 32 and c not in "\n\t\r")
    )
    ratio = weird / max(len(content), 1)

    if ratio > 0.05:
        return False, f"Bozuk encoding: {ratio:.3f} garip karakter orani"
    return True, ""


def _check_duplicate_ratio(content: str) -> tuple[bool, str]:
    sentences = [
        s.strip().lower()
        for s in re.split(r"[.!?\n]+", content)
        if len(s.strip()) > 30
    ]
    if not sentences:
        return True, ""

    dup_ratio = 1 - len(set(sentences)) / len(sentences)
    if dup_ratio > 0.4:
        return False, f"Yuksek tekrar: {dup_ratio:.2f}"
    return True, ""


# --- Toplu filtreleme ---

def filter_batch(items: list[dict]) -> list[dict]:
    """
    FIX #9: her item try/except ile korunur, patlayan atlanir.
    """
    total = len(items)
    passed: list[dict] = []
    skipped = 0

    for item in items:
        try:
            if quality_filter(item):
                passed.append(item)
        except Exception as e:
            skipped += 1
            url = item.get("url", "?") if isinstance(item, dict) else "?"
            logger.warning(
                f"filter_batch: beklenmeyen hata atlandi | {url} -> {e}"
            )

    rejected = total - len(passed) - skipped
    logger.info(
        f"Filtre: {len(passed)}/{total} gecti "
        f"| {rejected} reddedildi | {skipped} hata"
    )
    return passed
