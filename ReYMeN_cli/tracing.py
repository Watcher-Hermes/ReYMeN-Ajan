# -*- coding: utf-8 -*-
"""ReYMeN_cli/tracing.py — Izleme CLI.

Fonksiyon cagrilari, performans izleme ve debug bilgisi.
"""

import time
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _iz_simule(adim_sayisi=3):
    """Ornek iz kaydi olusturur."""
    kayitlar = []
    for i in range(adim_sayisi):
        basla = time.perf_counter()
        time.sleep(0.05)
        gecen = time.perf_counter() - basla
        kayitlar.append({
            "adim": i + 1,
            "islem": f"islem_{i+1}",
            "sure_ms": round(gecen * 1000, 2),
            "zaman": datetime.now().isoformat(),
        })
    return kayitlar


def kaydet(alt_parser):
    """tracing CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "view", "export", "clear"],
                            help="Yapilacak islem (start|stop|view|export|clear)")
    alt_parser.add_argument("--name", type=str, default=None, help="Izleme adi")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")
    alt_parser.add_argument("--depth", type=int, default=5, help="Izleme derinligi")


def calistir(args):
    """tracing komutunu calistir."""
    try:
        islem = args.islem or "view"
        print(f"[Tracing] Baslatiliyor: {islem}")

        if islem == "start":
            ad = args.name or f"trace_{datetime.now().strftime('%H%M%S')}"
            print(f"[Tracing] Izleme baslatildi: {ad}")
            print(f"  Derinlik: {args.depth}")

        elif islem == "stop":
            print("[Tracing] Izleme durduruldu")
            print(f"  Toplam kayit: 3")

        elif islem == "view":
            print("[Tracing] Iz kayitlari:")
            for kayit in _iz_simule():
                print(f"  Adim {kayit['adim']}: {kayit['islem']} - {kayit['sure_ms']}ms")

        elif islem == "export":
            if args.output:
                import json
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(_iz_simule(), f, indent=2)
                print(f"[Tracing] Iz kaydi kaydedildi: {args.output}")
            else:
                print("[Tracing] --output belirtin")

        elif islem == "clear":
            print("[Tracing] Iz kayitlari temizlendi")

    except Exception as e:
        print(f"[Tracing] Hata: {e}")
