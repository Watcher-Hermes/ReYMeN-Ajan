# -*- coding: utf-8 -*-
"""ReYMeN_cli/cache.py — Onbellek Yonetim CLI.

Veri onbellekleme, temizleme, listeleme ve istatistik.
"""

import json
import time
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
CACHE_DIZIN = PROJE_KOK / ".ReYMeN" / "cache"


def _cache_boyutu():
    """Onbellek boyutunu hesaplar."""
    toplam = 0
    dosya_sayisi = 0
    if CACHE_DIZIN.exists():
        for dosya in CACHE_DIZIN.rglob("*"):
            if dosya.is_file():
                toplam += dosya.stat().st_size
                dosya_sayisi += 1
    return toplam, dosya_sayisi


def kaydet(alt_parser):
    """cache CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["clear", "stats", "list", "warm", "config"],
                            help="Yapilacak islem (clear|stats|list|warm|config)")
    alt_parser.add_argument("--key", type=str, default=None, help="Onbellek anahtari")
    alt_parser.add_argument("--ttl", type=int, default=3600, help="Yasam suresi (saniye)")
    alt_parser.add_argument("--all", action="store_true", help="Tumunu temizle")


def calistir(args):
    """cache komutunu calistir."""
    try:
        islem = args.islem or "stats"
        print(f"[Cache] Baslatiliyor: {islem}")

        if islem == "clear":
            if args.all:
                import shutil
                if CACHE_DIZIN.exists():
                    shutil.rmtree(str(CACHE_DIZIN))
                    print("[Cache] Tum onbellek temizlendi")
                else:
                    print("[Cache] Onbellek dizini yok")
            elif args.key:
                hedef = CACHE_DIZIN / args.key
                if hedef.exists():
                    hedef.unlink()
                    print(f"[Cache] Silindi: {args.key}")
                else:
                    print(f"[Cache] Bulunamadi: {args.key}")
            else:
                print("[Cache] --key veya --all belirtin")

        elif islem == "stats":
            boyut, sayi = _cache_boyutu()
            print(f"[Cache] Istatistik:")
            print(f"  Dosya sayisi: {sayi}")
            print(f"  Toplam boyut: {boyut} B ({boyut/1024:.1f} KB)")
            print(f"  Dizin: {CACHE_DIZIN}")

        elif islem == "list":
            print("[Cache] Onbellek dosyalari:")
            if CACHE_DIZIN.exists():
                for dosya in sorted(CACHE_DIZIN.iterdir()):
                    if dosya.is_file():
                        boyut = dosya.stat().st_size
                        print(f"  {dosya.name} ({boyut}B)")
            else:
                print("  (bos)")

        elif islem == "warm":
            print("[Cache] Onbellek isitiliyor...")
            CACHE_DIZIN.mkdir(parents=True, exist_ok=True)
            print("[Cache] Isitma tamam")

        elif islem == "config":
            print("[Cache] Yapilandirma:")
            print(f"  Dizin: {CACHE_DIZIN}")
            print(f"  Varsayilan TTL: {args.ttl}s")
            print(f"  Max boyut: sinirsiz")

    except Exception as e:
        print(f"[Cache] Hata: {e}")
