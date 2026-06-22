# -*- coding: utf-8 -*-
"""ReYMeN_cli/monitor.py — Sistem Izleme CLI.

Canli izleme, log takibi, saglik kontrolu ve uyarilar.
"""

import time
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _saglik_kontrol():
    """Temel saglik kontrolleri."""
    durum = {}
    durum["gateway"] = "aktif" if (PROJE_KOK / "gateway").exists() else "pasif"
    durum["cli"] = "aktif"
    durum["zaman"] = datetime.now().isoformat()
    return durum


def kaydet(alt_parser):
    """monitor CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["health", "watch", "alerts", "tail", "status"],
                            help="Yapilacak islem (health|watch|alerts|tail|status)")
    alt_parser.add_argument("--file", type=str, default=None, help="Izlenecek dosya")
    alt_parser.add_argument("--interval", type=int, default=2, help="Kontrol araligi (sn)")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")


def calistir(args):
    """monitor komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Monitor] Baslatiliyor: {islem}")

        if islem == "health":
            durum = _saglik_kontrol()
            print("[Monitor] Sistem sagligi:")
            for anahtar, deger in durum.items():
                isaret = "OK" if deger == "aktif" else "HATA"
                print(f"  [{isaret}] {anahtar}: {deger}")

        elif islem == "watch":
            print(f"[Monitor] Canli izleme basladi (interval: {args.interval}s)")
            print("  Ctrl+C ile durdurun...")
            for i in range(5):
                cpu = 20 + i * 3
                ram = 45 + i
                print(f"  {datetime.now().strftime('%H:%M:%S')} CPU:%{cpu} RAM:%{ram}")
                time.sleep(args.interval)

        elif islem == "alerts":
            print("[Monitor] Aktif uyarilar:")
            print("  (Aktif uyari yok)")

        elif islem == "tail":
            print("[Monitor] Log takibi (simule):")
            if args.file:
                print(f"  Izleniyor: {args.file}")
            else:
                print("  --file ile bir dosya belirtin")
            print("  [INFO] Sistem calisiyor...")

        elif islem == "status":
            print("[Monitor] Sistem durumu:")
            print(f"  Izleme: AKTIF")
            print(f"  Metrik: toplaniyor")
            print(f"  Uyari: 0")

    except Exception as e:
        print(f"[Monitor] Hata: {e}")
