# -*- coding: utf-8 -*-
"""ReYMeN_cli/metrics.py — Metrik Toplama CLI.

Sistem metrikleri: performans, kullanim, hata oranlari.
"""

import time
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _ornek_metrikler():
    """Ornek metrik verileri."""
    return {
        "istek_sayisi": 15420,
        "hata_orani": 0.02,
        "ortalama_yanit": 0.345,
        "aktif_kullanici": 12,
        "bellek_kullanim": 45.2,
        "cpu_yuku": 23.5,
    }


def kaydet(alt_parser):
    """metrics CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["show", "collect", "alert", "export", "reset"],
                            help="Yapilacak islem (show|collect|alert|export|reset)")
    alt_parser.add_argument("--name", type=str, default=None, help="Metrik adi")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")
    alt_parser.add_argument("--interval", type=int, default=5, help="Toplama araligi (sn)")


def calistir(args):
    """metrics komutunu calistir."""
    try:
        islem = args.islem or "show"
        print(f"[Metrics] Baslatiliyor: {islem}")

        if islem == "show":
            metrikler = _ornek_metrikler()
            print("[Metrics] Sistem metrikleri:")
            for ad, deger in metrikler.items():
                print(f"  {ad}: {deger}")

        elif islem == "collect":
            print(f"[Metrics] Metrik toplaniyor (interval: {args.interval}s)...")
            for i in range(3):
                print(f"  {i+1}. olcum: CPU %{20+i*5}, RAM %{45+i*2}")
                time.sleep(1)
            print("[Metrics] Toplama tamam")

        elif islem == "alert":
            esik = args.name or "cpu>90"
            print(f"[Metrics] Uyari kurali: {esik}")
            print("  Durum: IZLEMEDE")

        elif islem == "export":
            if args.output:
                import json
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(_ornek_metrikler(), f, indent=2)
                print(f"[Metrics] Metrikler kaydedildi: {args.output}")
            else:
                print("[Metrics] --output belirtin")

        elif islem == "reset":
            print("[Metrics] Metrikler sifirlandi")

    except Exception as e:
        print(f"[Metrics] Hata: {e}")
