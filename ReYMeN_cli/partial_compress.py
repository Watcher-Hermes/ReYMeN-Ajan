# -*- coding: utf-8 -*-
"""ReYMeN_cli/partial_compress.py — Kismi Sikistirma CLI.

Dosya, dizin ve tum proje sikistirma, durum
sorgulama ve geri alma islemleri.
"""

import os
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _sikistirilan_oku() -> list:
    """Sikistirilan dosya kaydini oku."""
    dosya = PROJE_KOK / ".ReYMeN" / "compress" / "kayit.json"
    if not dosya.exists():
        return []
    try:
        import json
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except Exception:
        return []


def kaydet(alt_parser):
    """Kismi sikistirma CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: file, dir, all, status, undo
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["file", "dir", "all", "status", "undo"],
                            help="Yapilacak islem (file|dir|all|status|undo)")
    alt_parser.add_argument("--yol", type=str, default=None,
                            help="Dosya veya dizin yolu (file/dir/undo icin)")
    alt_parser.add_argument("--seviye", type=int, default=6,
                            help="Sikistirma seviyesi (1-9)")


def calistir(args):
    """Kismi sikistirma komutunu calistir."""
    try:
        islem = args.islem or "status"
        seviye = args.seviye

        if islem == "file":
            yol = args.yol
            if not yol:
                print("[PartialCompress] Lutfen --yol parametresini belirtin.")
                return
            print(f"[PartialCompress] '{yol}' sikistiriliyor (seviye: {seviye})...")

        elif islem == "dir":
            yol = args.yol or "."
            print(f"[PartialCompress] '{yol}' dizini sikistiriliyor (seviye: {seviye})...")

        elif islem == "all":
            print(f"[PartialCompress] Tum proje sikistiriliyor (seviye: {seviye})...")

        elif islem == "status":
            kayit = _sikistirilan_oku()
            print(f"[PartialCompress] Sikistirma durumu:")
            print(f"  Sikistirilan dosya: {len(kayit)}")
            print(f"  Toplam kazanc: 0 MB")

        elif islem == "undo":
            yol = args.yol or "son"
            print(f"[PartialCompress] '{yol}' geri aliniyor...")

    except Exception as e:
        print(f"[PartialCompress] Beklenmeyen hata: {e}")
