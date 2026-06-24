# -*- coding: utf-8 -*-
"""error_classifier.py — ReYMeN hata siniflandirma modulu.

LLM yanitlarinda/agent akisinda karsilasilan hatalari kategorize eder.
Her hata bir `HataKategori` enum'una ve opsiyonel cozum onerisine
map edilir. Ayrica test import'larinda kullanilmak uzere `SyntaxError`
tespiti icin de kullanilabilir.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class HataKategori(str, Enum):
    """ReYMeN hata kategorileri."""

    BILINMEYEN = "bilinmiyor"
    SYNTAX = "syntax"
    IMPORT = "import"
    API = "api"
    SUBPROCESS = "subprocess"
    MEMORY = "hafiza"
    TOR = "tor"
    ZAMAN_ASIMI = "timeout"
    IZIN = "yetki"
    AG = "ag"
    DISK = "disk"
    MODUL_EKSIK = "modul_eksik"


@dataclass
class HataBilgisi:
    """Siniflandirilmis hata bilgisi."""

    kategori: HataKategori = HataKategori.BILINMEYEN
    kaynak: str = ""
    mesaj: str = ""
    cozum: str = ""
    etiketler: list[str] = field(default_factory=list)


# ── Regex kalıpları (hata mesajından kategori tespiti) ──────────────
_KATEGORI_KALIPLARI: dict[HataKategori, list[re.Pattern]] = {
    HataKategori.SYNTAX: [
        re.compile(r"SyntaxError", re.I),
        re.compile(r"IndentationError", re.I),
        re.compile(r"invalid syntax", re.I),
    ],
    HataKategori.IMPORT: [
        re.compile(r"ModuleNotFoundError", re.I),
        re.compile(r"ImportError", re.I),
        re.compile(r"No module named", re.I),
    ],
    HataKategori.API: [
        re.compile(r"HTTPError", re.I),
        re.compile(r"ConnectionError", re.I),
        re.compile(r"requests\.exceptions", re.I),
        re.compile(r"httpx", re.I),
        re.compile(r"api.*key", re.I),
        re.compile(r"429|401|403|500", re.I),
    ],
    HataKategori.SUBPROCESS: [
        re.compile(r"subprocess\.(CalledProcessError|TimeoutExpired)", re.I),
        re.compile(r"FileNotFoundError.*No such file or directory", re.I),
    ],
    HataKategori.MEMORY: [
        re.compile(r"MemoryError", re.I),
        re.compile(r"OutOfMemory", re.I),
        re.compile(r"cannot allocate", re.I),
        re.compile(r"CUDA.*out of memory", re.I),
    ],
    HataKategori.TOR: [
        re.compile(r"tor", re.I),
        re.compile(r"socks5", re.I),
        re.compile(r"Tor.*connection", re.I),
    ],
    HataKategori.ZAMAN_ASIMI: [
        re.compile(r"Timeout", re.I),
        re.compile(r"timed out", re.I),
    ],
    HataKategori.IZIN: [
        re.compile(r"PermissionError", re.I),
        re.compile(r"AccessDenied", re.I),
        re.compile(r"permission denied", re.I),
    ],
    HataKategori.MODUL_EKSIK: [
        re.compile(r"No module named", re.I),
        re.compile(r"cannot import name", re.I),
    ],
}


# ── Çözüm önerileri ─────────────────────────────────────────────────
_COZUM_Onerisi: dict[HataKategori, str] = {
    HataKategori.SYNTAX: "Kodda yazim hatasi. `compile()` ile dogrulayin.",
    HataKategori.IMPORT: "Eksik bagimlilik. `uv add` veya `pip install` ile kurun.",
    HataKategori.API: "API anahtari / erisim sorunu. `.env` ve token'lari kontrol edin.",
    HataKategori.SUBPROCESS: "Dis arac calistirilamadi. Yol/izin kontrol edin.",
    HataKategori.MEMORY: "Bellek yetersiz. Batch boyutunu kucultun / modeli hafifletin.",
    HataKategori.TOR: "Tor baglantisi basarisiz. Tor servisini baslatmayi deneyin.",
    HataKategori.ZAMAN_ASIMI: "Islem cok uzun surdu. Zaman asimi degerini artirin.",
    HataKategori.IZIN: "Dosya/klasor izni yok. chmod / yonetici hakki kontrol edin.",
    HataKategori.MODUL_EKSIK: "Modul yuklenemiyor. Bagimliligi kurun veya __init__'e ekleyin.",
    HataKategori.AG: "Baglanti sorunu. VPN/firewall/internet baglantisini kontrol edin.",
    HataKategori.DISK: "Disk dolu veya yazma izni yok. Alan kontrol edin.",
}


def siniflandir(hata_mesaji: str, kaynak: str = "") -> HataBilgisi:
    """Hata mesajini analiz edip kategorize eder."""
    bilgi = HataBilgisi(kategori=HataKategori.BILINMEYEN, kaynak=kaynak, mesaj=hata_mesaji[:200])

    if not hata_mesaji:
        return bilgi

    for kategori, kalıplar in _KATEGORI_KALIPLARI.items():
        for kalıp in kalıplar:
            if kalıp.search(hata_mesaji):
                bilgi.kategori = kategori
                bilgi.cozum = _COZUM_Onerisi.get(kategori, "")
                bilgi.etiketler.append(kategori.value)
                return bilgi

    return bilgi


def syntax_kontrol(dosya_yolu: str) -> Optional[HataBilgisi]:
    """Bir dosyada Python syntax hatasi olup olmadigini kontrol eder.

    Kullanimi::

        sonuc = syntax_kontrol(\"reymen/sistem/main.py\")
        if sonuc:
            print(f\"HATA: {sonuc.mesaj}\")
        else:
            print(\"Temiz\")
    """
    try:
        with open(dosya_yolu, "rb") as f:
            raw = f.read()
        # BOM kontrolü
        if raw[:3] == b"\xef\xbb\xbf":
            return HataBilgisi(
                kategori=HataKategori.SYNTAX,
                kaynak=dosya_yolu,
                mesaj="BOM (U+FEFF) tespit edildi",
                cozum="Dosyayi UTF-8 BOM olmadan kaydedin.",
                etiketler=["bom"],
            )
        compile(raw, dosya_yolu, "exec")
        return None
    except SyntaxError as e:
        return HataBilgisi(
            kategori=HataKategori.SYNTAX,
            kaynak=dosya_yolu,
            mesaj=f"Satir {e.lineno}: {e.msg}",
            cozum=_COZUM_Onerisi[HataKategori.SYNTAX],
            etiketler=[f"satir_{e.lineno}"],
        )
    except Exception as e:
        return HataBilgisi(
            kategori=HataKategori.BILINMEYEN,
            kaynak=dosya_yolu,
            mesaj=str(e),
        )


def topla_syntax(dizin: str, desen: str = "*.py") -> list[HataBilgisi]:
    """Bir dizindeki tum .py dosyalarinda syntax hatasi taramasi yapar."""
    from pathlib import Path

    hatalar: list[HataBilgisi] = []
    for dosya in Path(dizin).rglob(desen):
        sonuc = syntax_kontrol(str(dosya))
        if sonuc:
            hatalar.append(sonuc)
    return hatalar
