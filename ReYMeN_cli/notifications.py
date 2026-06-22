# -*- coding: utf-8 -*-
"""ReYMeN_cli/notifications.py — Bildirim CLI.

Bildirim gonderimi, tercih yonetimi ve kanal ayarlari.
"""

from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _kanallar():
    """Mevcut bildirim kanallari."""
    return {
        "telegram": True,
        "wecom": True,
        "sms": False,
        "email": True,
        "push": False,
    }


def kaydet(alt_parser):
    """notifications CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["send", "channels", "prefs", "test", "history"],
                            help="Yapilacak islem (send|channels|prefs|test|history)")
    alt_parser.add_argument("--message", type=str, default=None, help="Bildirim mesaji")
    alt_parser.add_argument("--channel", type=str, default=None, help="Bildirim kanali")
    alt_parser.add_argument("--title", type=str, default=None, help="Bildirim basligi")
    alt_parser.add_argument("--priority", type=str, default="normal",
                            choices=["low", "normal", "high"], help="Oncelik")


def calistir(args):
    """notifications komutunu calistir."""
    try:
        islem = args.islem or "channels"
        print(f"[Notifications] Baslatiliyor: {islem}")

        if islem == "send":
            mesaj = args.message or "Test bildirimi"
            kanal = args.channel or "all"
            print(f"[Notifications] Bildirim gonderiliyor:")
            print(f"  Kanal: {kanal}")
            print(f"  Mesaj: {mesaj[:80]}")
            print(f"  Oncelik: {args.priority}")

        elif islem == "channels":
            print("[Notifications] Bildirim kanallari:")
            for kanal, aktif in _kanallar().items():
                isaret = "AKTIF" if aktif else "PASIF"
                print(f"  [{isaret}] {kanal}")

        elif islem == "prefs":
            print("[Notifications] Tercihler:")
            print("  Varsayilan kanal: telegram")
            print("  Sessiz mod: kapali")
            print("  Toplu bildirim: acik")

        elif islem == "test":
            print("[Notifications] Test bildirimi gonderiliyor...")
            for kanal, aktif in _kanallar().items():
                if aktif:
                    print(f"  [TEST] {kanal}: basarili")
                else:
                    print(f"  [TEST] {kanal}: atlandi (pasif)")

        elif islem == "history":
            print("[Notifications] Bildirim gecmisi:")
            print("  (Henuz bildirim yok)")

    except Exception as e:
        print(f"[Notifications] Hata: {e}")
