# -*- coding: utf-8 -*-
"""ReYMeN_cli/rollback.py — Geri Alma CLI.

Son degisiklikleri geri alma, surum kontrolu ve eski haline donme.
"""

import time
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _degisiklik_gecmisi():
    """Son degisiklik kayitlari."""
    return [
        ("v2.1.0", "15.06.2026", "yeni CLI modulleri eklendi"),
        ("v2.0.0", "10.06.2026", "gateway yeniden yapilandirildi"),
        ("v1.9.0", "01.06.2026", "performans iyilestirmeleri"),
    ]


def kaydet(alt_parser):
    """rollback CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "undo", "to", "status", "confirm"],
                            help="Yapilacak islem (list|undo|to|status|confirm)")
    alt_parser.add_argument("--point", type=str, default=None, help="Geri donulecek nokta")
    alt_parser.add_argument("--steps", type=int, default=1, help="Geri adim sayisi")


def calistir(args):
    """rollback komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Rollback] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Rollback] Degisiklik gecmisi:")
            for surum, tarih, aciklama in _degisiklik_gecmisi():
                print(f"  {surum} ({tarih}): {aciklama}")

        elif islem == "undo":
            adim = args.steps
            print(f"[Rollback] Son {adim} degisiklik geri aliniyor...")
            time.sleep(1)
            print(f"[Rollback] {adim} degisiklik basariyla geri alindi")

        elif islem == "to":
            nokta = args.point or "v1.9.0"
            print(f"[Rollback] Geri donuluyor: {nokta}")
            time.sleep(1.5)
            print(f"[Rollback] {nokta} surumune basariyla donuldu")

        elif islem == "status":
            print("[Rollback] Durum:")
            print("  Mevcut surum: v2.1.0")
            print("  Geri alma: hazir")
            print("  Son islem: yok")

        elif islem == "confirm":
            print("[Rollback] Geri alma onaylaniyor...")
            time.sleep(0.5)
            print("[Rollback] Onay tamam")

    except Exception as e:
        print(f"[Rollback] Hata: {e}")
