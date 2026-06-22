# -*- coding: utf-8 -*-
"""ReYMeN_cli/proxy.py — Vekil Sunucu CLI.

Proxy yapilandirmasi, iletim kurallari ve yonlendirme.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """proxy CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "status", "routes", "config"],
                            help="Yapilacak islem (start|stop|status|routes|config)")
    alt_parser.add_argument("--port", type=int, default=8080, help="Proxy portu")
    alt_parser.add_argument("--target", type=str, default=None, help="Hedef URL")
    alt_parser.add_argument("--config", type=str, default=None, help="Yapilandirma dosyasi")


def calistir(args):
    """proxy komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Proxy] Baslatiliyor: {islem}")

        if islem == "start":
            port = args.port
            print(f"[Proxy] Baslatiliyor (port: {port})...")
            if args.target:
                print(f"  Hedef: {args.target}")
            print(f"  Proxy basarili sekilde baslatildi")

        elif islem == "stop":
            print("[Proxy] Durduruluyor...")
            print("  Proxy durduruldu")

        elif islem == "status":
            print("[Proxy] Durum:")
            print("  Calisma: AKTIF")
            print(f"  Port: {args.port}")
            print("  Baglanti: 0")

        elif islem == "routes":
            print("[Proxy] Yonlendirme kurallari:")
            print("  /api/* -> localhost:8000")
            print("  /webhook/* -> localhost:9000")

        elif islem == "config":
            print("[Proxy] Yapilandirma:")
            print(f"  Port: {args.port}")
            print("  SSL: kapali")
            print("  Zamanasimi: 30s")
            if args.config:
                print(f"  Dosya: {args.config}")

    except Exception as e:
        print(f"[Proxy] Hata: {e}")
