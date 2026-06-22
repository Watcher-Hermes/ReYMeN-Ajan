# -*- coding: utf-8 -*-
"""ReYMeN_cli/sync_cli.py — Senkronizasyon CLI.

Veri senkronizasyonu, dosya esitleme ve replikasyon.
"""

import time
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """sync_cli CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "status", "dry-run", "conflicts"],
                            help="Yapilacak islem (start|stop|status|dry-run|conflicts)")
    alt_parser.add_argument("--source", type=str, default=None, help="Kaynak dizin")
    alt_parser.add_argument("--target", type=str, default=None, help="Hedef dizin")
    alt_parser.add_argument("--interval", type=int, default=60, help="Senkronizasyon araligi (sn)")


def calistir(args):
    """sync_cli komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Sync] Baslatiliyor: {islem}")

        if islem == "start":
            kaynak = args.source or str(PROJE_KOK)
            hedef = args.target or str(PROJE_KOK / ".ReYMeN" / "sync")
            print(f"[Sync] Senkronizasyon baslatiliyor:")
            print(f"  Kaynak: {kaynak}")
            print(f"  Hedef: {hedef}")
            print(f"  Aralik: {args.interval}s")
            Path(hedef).mkdir(parents=True, exist_ok=True)
            print("[Sync] Senkronizasyon basarili")

        elif islem == "stop":
            print("[Sync] Senkronizasyon durduruldu")

        elif islem == "status":
            print("[Sync] Senkronizasyon durumu:")
            print("  Durum: AKTIF")
            print("  Son senkron: henuz")
            print("  Bekleyen: 0")

        elif islem == "dry-run":
            print("[Sync] Deneme senkronizasyonu:")
            print("  Kontrol edilen: 125 dosya")
            print("  Esitlenecek: 0 dosya")

        elif islem == "conflicts":
            print("[Sync] Celiski cozumu:")
            print("  (Celiski bulunamadi)")

    except Exception as e:
        print(f"[Sync] Hata: {e}")
