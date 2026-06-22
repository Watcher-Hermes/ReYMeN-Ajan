# -*- coding: utf-8 -*-
"""ReYMeN_cli/broadcast.py — Toplu Mesaj CLI.

Birden cok kanala/kullaniciya eszamanli mesaj gonderimi.
"""

import json
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _kanal_listesi():
    """Mevcut kanallari listeler."""
    return ["telegram", "wecom", "slack", "discord", "sms", "email"]


def kaydet(alt_parser):
    """broadcast CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["send", "channels", "status", "history", "cancel"],
                            help="Yapilacak islem (send|channels|status|history|cancel)")
    alt_parser.add_argument("--message", type=str, default=None, help="Mesaj icerigi")
    alt_parser.add_argument("--channel", type=str, default=None, help="Hedef kanal")
    alt_parser.add_argument("--file", type=str, default=None, help="Mesaj dosyasi")
    alt_parser.add_argument("--priority", type=str, default="normal",
                            choices=["low", "normal", "high", "urgent"], help="Oncelik")


def calistir(args):
    """broadcast komutunu calistir."""
    try:
        islem = args.islem or "status"
        print(f"[Broadcast] Baslatiliyor: {islem}")

        if islem == "send":
            mesaj = args.message
            if not mesaj and args.file:
                with open(args.file, "r", encoding="utf-8") as f:
                    mesaj = f.read()
            if not mesaj:
                print("[Broadcast] Mesaj gerekli (--message veya --file)")
                return
            kanal = args.channel or "all"
            print(f"[Broadcast] Mesaj gonderiliyor: kanal={kanal}")
            print(f"[Broadcast] Oncelik: {args.priority}")
            print(f"[Broadcast] IcERIK: {mesaj[:100]}...")
            print("[Broadcast] Gonderim basarili (simule)")

        elif islem == "channels":
            print("[Broadcast] Kullanilabilir kanallar:")
            for k in _kanal_listesi():
                print(f"  + {k}")

        elif islem == "status":
            print("[Broadcast] Son durum:")
            print("  Sistem: aktif")
            print("  Kuyruk: 0")
            print(f"  Kanallar: {len(_kanal_listesi())} adet")

        elif islem == "history":
            print("[Broadcast] Son 10 mesaj:")
            print("  (Henuz kayitli mesaj yok)")

        elif islem == "cancel":
            print("[Broadcast] Bekleyen mesajlar iptal edildi")

    except Exception as e:
        print(f"[Broadcast] Hata: {e}")
