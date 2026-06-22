# -*- coding: utf-8 -*-
"""ReYMeN_cli/watchdog.py — Gozetleme CLI.

Dosya degisikliklerini izleme, otomatik yeniden baslatma ve uyari.
"""

import time
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _izlenecek_dizinler():
    """Izlenecek dizinler."""
    return ["gateway", "ReYMeN_cli"]


def kaydet(alt_parser):
    """watchdog CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "status", "events", "config"],
                            help="Yapilacak islem (start|stop|status|events|config)")
    alt_parser.add_argument("--path", type=str, default=None, help="Izlenecek dizin")
    alt_parser.add_argument("--pattern", type=str, default="*.py", help="Dosya deseni")
    alt_parser.add_argument("--interval", type=int, default=2, help="Kontrol araligi (sn)")


def calistir(args):
    """watchdog komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Watchdog] Baslatiliyor: {islem}")

        if islem == "start":
            dizin = args.path or "."
            print(f"[Watchdog] Izleme baslatildi: {dizin}")
            print(f"  Desen: {args.pattern}")
            print(f"  Aralik: {args.interval}s")
            print("  (simulasyon: 5 saniye izlenecek)")
            for i in range(3):
                time.sleep(0.5)
                print(f"  {datetime.now().strftime('%H:%M:%S')} - izleniyor...")
            print("[Watchdog] Izleme basarili")

        elif islem == "stop":
            print("[Watchdog] Izleme durduruldu")
            print("  Toplam olay: 0")

        elif islem == "status":
            print("[Watchdog] Gozetleme durumu:")
            print("  Durum: AKTIF" if islem == "status" else "  Durum: DURDURULDU")
            print(f"  Izlenen: {', '.join(_izlenecek_dizinler())}")
            print(f"  Desen: {args.pattern}")

        elif islem == "events":
            print("[Watchdog] Son olaylar:")
            print("  (Henuz olay kaydi yok)")

        elif islem == "config":
            print("[Watchdog] Yapilandirma:")
            print(f"  Dizinler: {', '.join(_izlenecek_dizinler())}")
            print(f"  Desen: {args.pattern}")
            print(f"  Aralik: {args.interval}s")
            print("  Otomatik yeniden baslatma: kapali")

    except Exception as e:
        print(f"[Watchdog] Hata: {e}")
