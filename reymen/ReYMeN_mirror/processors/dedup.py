"""
dedup.py — Duplicate icerik tespiti.

Metin benzerligini hesaplar (cosine similarity + simhash),
esik degerinin uzerindeki icerikleri tekillemek icin isaretler.
"""

import hashlib
import re
from collections import Counter
from typing import Optional

from loguru import logger

# Benzerlik esigi (%)
BENZERLIK_ESIGI: float = 0.75


def _temizle(metin: str) -> str:
    """Metni normalize et: kucuk harf, gereksiz bosluk, noktalama."""
    metin = metin.lower()
    metin = re.sub(r"[^\w\s]", " ", metin)
    metin = re.sub(r"\s+", " ", metin)
    return metin.strip()


def _kelime_kumesi(metin: str) -> set[str]:
    """Metnin kelime kumesini cikar (stopwords filtresiz)."""
    return set(_temizle(metin).split())


def _jaccard_benzerlik(metin1: str, metin2: str) -> float:
    """Jaccard benzerlik katsayisi: |A∩B| / |A∪B|."""
    kelime1 = _kelime_kumesi(metin1)
    kelime2 = _kelime_kumesi(metin2)

    kesisim = len(kelime1 & kelime2)
    birlesim = len(kelime1 | kelime2)

    if birlesim == 0:
        return 0.0

    return kesisim / birlesim


def _simhash(metin: str, bit: int = 64) -> int:
    """SimHash parmak izi hesapla."""
    kelimeler = _temizle(metin).split()
    v = [0] * bit

    for kelime in set(kelimeler):
        # Kelimenin hash'ini al
        h = int(hashlib.md5(kelime.encode()).hexdigest(), 16)
        for i in range(bit):
            if h & (1 << i):
                v[i] += 1
            else:
                v[i] -= 1

    fingerprint = 0
    for i in range(bit):
        if v[i] > 0:
            fingerprint |= (1 << i)

    return fingerprint


def _hamming_mesafe(h1: int, h2: int) -> int:
    """Iki SimHash arasindaki Hamming mesafesi."""
    return bin(h1 ^ h2).count("1")


def _simhash_benzerlik(h1: int, h2: int, bit: int = 64) -> float:
    """SimHash ile benzerlik puani (0.0 - 1.0)."""
    mesafe = _hamming_mesafe(h1, h2)
    return 1.0 - (mesafe / bit)


class Deduplicator:
    """Duplicate icerik tespiti ve yonetimi."""

    def __init__(self, esik: float = BENZERLIK_ESIGI):
        self.esik = esik
        self._gorulen: list[tuple[int, str]] = []  # (simhash, orijinal_metin)

    def deduplicate(self, icerik_listesi: list[dict]) -> list[dict]:
        """
        Icerik listesinden duplicateleri cikar.

        Args:
            icerik_listesi: [{"url", "baslik", "icerik", ...}, ...]

        Returns:
            Benzersiz icerikler
        """
        if not icerik_listesi:
            return []

        unique: list[dict] = []
        atilan: int = 0

        for item in icerik_listesi:
            icerik = item.get("icerik") or item.get("baslik", "")
            if not icerik:
                continue

            h = _simhash(icerik)
            is_duplicate = False

            for onceki_h, _ in self._gorulen:
                benzerlik = _simhash_benzerlik(h, onceki_h)
                if benzerlik >= self.esik:
                    is_duplicate = True
                    atilan += 1
                    logger.debug(f"dedup: atildi ({benzerlik:.2f} benzer) - {item.get('url', '?')}")
                    break

            if not is_duplicate:
                self._gorulen.append((h, icerik))
                unique.append(item)

        logger.info(f"deduplicate: {len(unique)} benzersiz, {atilan} atilan")
        return unique

    def reset(self) -> None:
        """Bellekteki gorulen icerikleri temizle."""
        self._gorulen.clear()
        logger.debug("dedup: resetlendi")


def cosine_benzerlik(metin1: str, metin2: str) -> float:
    """
    Cosine similarity (kelime frekansi vektorleri ile).
    Jaccard'dan daha hassas.
    """
    kelime1 = _temizle(metin1).split()
    kelime2 = _temizle(metin2).split()

    vec1 = Counter(kelime1)
    vec2 = Counter(kelime2)

    # Ortak kelimeler
    ortak = set(vec1.keys()) & set(vec2.keys())

    # Dot product
    dot = sum(vec1[k] * vec2[k] for k in ortak)

    # Magnitude
    mag1 = sum(v * v for v in vec1.values()) ** 0.5
    mag2 = sum(v * v for v in vec2.values()) ** 0.5

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot / (mag1 * mag2)


def esik_ustu_mu(metin1: str, metin2: str, esik: float = BENZERLIK_ESIGI) -> bool:
    """
    Iki metin arasinda benzerlik esiginin uzerinde mi?

    Hizli once Jaccard, esik uzerinde ise cosine ile dogrula.
    """
    # Hizli filtre: Jaccard
    j = _jaccard_benzerlik(metin1, metin2)
    if j < esik * 0.8:  # Jaccard genelde dustuk icin tolerans
        return False

    # Dogrulama: cosine
    c = cosine_benzerlik(metin1, metin2)
    return c >= esik
