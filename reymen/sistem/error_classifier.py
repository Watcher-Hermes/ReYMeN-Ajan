# -*- coding: utf-8 -*-
"""error_classifier.py — ReYMeN hata siniflandirma modulu.

LLM yanitlarinda/agent akisinda karsilasilan hatalari kategorize eder.
Her hata bir HataKategori enum'una ve opsiyonel cozum onerisine map edilir.
"""


from __future__ import annotations

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
    JSON = "json"
    YETKILENDIRME = "yetkilendirme"


@dataclass
class HataBilgisi:
    """Siniflandirilmis hata bilgisi."""

    kategori: HataKategori = HataKategori.BILINMEYEN
    kaynak: str = ""
    mesaj: str = ""
    cozum: str = ""
    etiketler: list[str] = field(default_factory=list)


def _k(l): return re.compile(l, re.I)


# -- Regex kaliplari --
_KATEGORI_KALIPLARI: dict[HataKategori, list[re.Pattern]] = {
    HataKategori.SYNTAX: [
        _k(r"SyntaxError"),
        _k(r"IndentationError"),
        _k(r"invalid syntax"),
        _k(r"TabError"),
    ],
    HataKategori.IMPORT: [
        _k(r"ModuleNotFoundError"),
        _k(r"ImportError"),
        _k(r"No module named"),
    ],
    HataKategori.YETKILENDIRME: [
        _k(r"Unauthorized"),
        _k(r"AuthenticationError"),
        _k(r"invalid.*token"),
        _k(r"invalid.*api[_\s]?key"),
        _k(r"auth.*failed"),
    ],
    HataKategori.API: [
        _k(r"HTTPError"),
        _k(r"ConnectionError"),
        _k(r"requests\.exceptions"),
        _k(r"httpx"),
        _k(r"\bapi[_\s]?key\b"),
        _k(r"429|401|403|500"),
    ],
    HataKategori.SUBPROCESS: [
        _k(r"subprocess\.(CalledProcessError|TimeoutExpired)"),
        _k(r"FileNotFoundError.*No such file or directory"),
        _k(r"returned non-zero exit status"),
        _k(r"Command '.*' returned non-zero"),
    ],
    HataKategori.MEMORY: [
        _k(r"MemoryError"),
        _k(r"OutOfMemory"),
        _k(r"cannot allocate"),
        _k(r"CUDA.*out of memory"),
    ],
    HataKategori.TOR: [
        _k(r"\bTor\b"),
        _k(r"socks5"),
        _k(r"Tor.*connection"),
        _k(r"socks.*proxy"),
    ],
    HataKategori.ZAMAN_ASIMI: [
        _k(r"Timeout"),
        _k(r"timed out"),
        _k(r"deadline exceeded"),
    ],
    HataKategori.IZIN: [
        _k(r"PermissionError"),
        _k(r"AccessDenied"),
        _k(r"permission denied"),
    ],
    HataKategori.YETKILENDIRME: [
        _k(r"Unauthorized"),
        _k(r"AuthenticationError"),
        _k(r"invalid.*token"),
        _k(r"invalid.*api.*key"),
        _k(r"auth.*failed"),
    ],
    HataKategori.AG: [
        _k(r"ConnectionRefused"),
        _k(r"Connection refused"),
        _k(r"Network unreachable"),
        _k(r"ENETUNREACH"),
        _k(r"Name or service not known"),
        _k(r"getaddrinfo"),
        _k(r"no route to host"),
        _k(r"connection reset"),
        _k(r"broken pipe"),
    ],
    HataKategori.DISK: [
        _k(r"No space left on device"),
        _k(r"ENOSPC"),
        _k(r"Disk full"),
        _k(r"Quota exceeded"),
        _k(r"disk.*full"),
    ],
    HataKategori.MODUL_EKSIK: [
        _k(r"No module named"),
        _k(r"cannot import name"),
    ],
    HataKategori.JSON: [
        _k(r"JSONDecodeError"),
        _k(r"json\.decoder"),
        _k(r"Expecting value.*line"),
        _k(r"Extra data.*line"),
        _k(r"Unterminated string"),
    ],
}

_COZUM_Onerisi: dict[HataKategori, str] = {
    HataKategori.SYNTAX: "Kodda yazim hatasi. `compile()` ile dogrulayin.",
    HataKategori.IMPORT: "Eksik bagimlilik. `uv add` veya `pip install` ile kurun.",
    HataKategori.API: "API anahtari / erisim sorunu. `.env` ve token'lari kontrol edin.",
    HataKategori.SUBPROCESS: "Dis arac calistirilamadi. Yol/izin kontrol edin.",
    HataKategori.MEMORY: "Bellek yetersiz. Batch boyutunu kucultun / modeli hafifletin.",
    HataKategori.TOR: "Tor baglantisi basarisiz. Tor servisini baslatmayi deneyin.",
    HataKategori.ZAMAN_ASIMI: "Islem cok uzun surdu. Zaman asimi degerini artirin.",
    HataKategori.IZIN: "Dosya/klasor izni yok. chmod / yonetici hakki kontrol edin.",
    HataKategori.YETKILENDIRME: "Kimlik dogrulama sorunu. API anahtari / token gecerliligini kontrol edin.",
    HataKategori.MODUL_EKSIK: "Modul yuklenemiyor. Bagimliligi kurun veya __init__'e ekleyin.",
    HataKategori.AG: "Baglanti sorunu. VPN/firewall/internet baglantisini kontrol edin.",
    HataKategori.DISK: "Disk dolu veya yazma izni yok. Alan kontrol edin.",
    HataKategori.JSON: "JSON ayristirma hatasi. Ciktiyi gecerli JSON ile karsilastirin.",
}


def siniflandir(hata_mesaji: str, kaynak: str = "") -> HataBilgisi:
    """Hata mesajini analiz edip kategorize eder."""
    bilgi = HataBilgisi(
        kategori=HataKategori.BILINMEYEN,
        kaynak=kaynak,
        mesaj=hata_mesaji[:200],
    )

    if not hata_mesaji:
        return bilgi

    for kategori, kaliplar in _KATEGORI_KALIPLARI.items():
        for kaliip in kaliplar:
            if kaliip.search(hata_mesaji):
                bilgi.kategori = kategori
                bilgi.cozum = _COZUM_Onerisi.get(kategori, "")
                bilgi.etiketler.append(kategori.value)
                return bilgi

    return bilgi


def syntax_kontrol(dosya_yolu: str) -> Optional[HataBilgisi]:
    """Bir dosyada Python syntax hatasi olup olmadigini kontrol eder.

    Kullanimi::

        sonuc = syntax_kontrol("reymen/sistem/main.py")
        if sonuc:
            print(f"HATA: {sonuc.mesaj}")
        else:
            print("Temiz")
    """
    try:
        with open(dosya_yolu, "rb") as f:
            raw = f.read()
        # BOM kontrolu
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
    except MemoryError:
        return HataBilgisi(
            kategori=HataKategori.MEMORY,
            kaynak=dosya_yolu,
            mesaj="Dosya cok buyuk, okunamadi",
            cozum=_COZUM_Onerisi[HataKategori.MEMORY],
        )
    except Exception as e:
        return HataBilgisi(
            kategori=HataKategori.BILINMEYEN,
            kaynak=dosya_yolu,
            mesaj=str(e),
        )


def trace_parser(traceback_text: str) -> list[dict]:
    """Traceback metninden dosya, satir ve hata mesaji cikarir.

    Ornek::

        trace_parser(traceback.format_exc())
        # -> [{"dosya": "main.py", "satir": 42, "fonksiyon": "run", "mesaj": "..."}]
    """
    sonuclar: list[dict] = []
    # Kaliplar: File "x/y.py", line 42, in fonksiyon
    for match in re.finditer(
        r'File\s+"([^"]+)",\s+line\s+(\d+)(?:,\s+in\s+(\w+))?',
        traceback_text,
    ):
        sonuclar.append({
            "dosya": match.group(1),
            "satir": int(match.group(2)),
            "fonksiyon": match.group(3) or "?",
        })

    # Son hatayi bul (en sondaki: ErrorType: message)
    hata_match = re.search(
        r"(\w+(?:\.\w+)*Error|Exception|Warning|SystemExit):\s*(.+?)$",
        traceback_text,
        re.MULTILINE,
    )
    if hata_match:
        if sonuclar:
            sonuclar[-1]["hata_turu"] = hata_match.group(1)
            sonuclar[-1]["mesaj"] = hata_match.group(2).strip()

    return sonuclar


def topla_syntax(dizin: str, desen: str = "*.py") -> list[HataBilgisi]:
    """Bir dizindeki tum .py dosyalarinda syntax hatasi taramasi yapar."""
    from pathlib import Path

    hatalar: list[HataBilgisi] = []
    for dosya in Path(dizin).rglob(desen):
        sonuc = syntax_kontrol(str(dosya))
        if sonuc:
            hatalar.append(sonuc)
    return hatalar
