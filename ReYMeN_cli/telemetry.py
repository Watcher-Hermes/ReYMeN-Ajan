# -*- coding: utf-8 -*-
"""ReYMeN_cli/telemetry.py — Telemetri CLI.

Sistem verisi toplama, analiz ve raporlama.
"""

from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _sistem_bilgisi():
    """Temel sistem bilgisi toplar."""
    import sys, platform
    return {
        "zaman": datetime.now().isoformat(),
        "python": sys.version.split()[0],
        "platform": platform.system(),
        "makine": platform.node(),
    }


def kaydet(alt_parser):
    """telemetry CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["collect", "send", "status", "config", "clear"],
                            help="Yapilacak islem (collect|send|status|config|clear)")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")
    alt_parser.add_argument("--enable", action="store_true", help="Telemetriyi aktif et")
    alt_parser.add_argument("--disable", action="store_true", help="Telemetriyi devre disi birak")


def calistir(args):
    """telemetry komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Telemetry] Baslatiliyor: {islem}")

        if islem == "collect":
            print("[Telemetry] Veri toplaniyor...")
            bilgi = _sistem_bilgisi()
            for anahtar, deger in bilgi.items():
                print(f"  {anahtar}: {deger}")
            if args.output:
                import json
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(bilgi, f, indent=2)
                print(f"  Kaydedildi: {args.output}")

        elif islem == "send":
            print("[Telemetry] Veri gonderiliyor...")
            bilgi = _sistem_bilgisi()
            print(f"  Gonderilen: {len(bilgi)} alan")
            print("  Gonderim basarili (simule)")

        elif islem == "status":
            print("[Telemetry] Telemetri durumu:")
            print("  Durum: AKTIF")
            print("  Son gonderim: henuz")
            print("  Toplanan veri: sistem bilgisi")

        elif islem == "config":
            if args.enable:
                print("[Telemetry] Telemetri aktif edildi")
            elif args.disable:
                print("[Telemetry] Telemetri devre disi birakildi")
            else:
                print("[Telemetry] Mevcut yapilandirma:")
                print("  Veri toplama: acik")
                print("  Otomatik gonderim: kapali")

        elif islem == "clear":
            print("[Telemetry] Toplanan veri temizlendi")

    except Exception as e:
        print(f"[Telemetry] Hata: {e}")
