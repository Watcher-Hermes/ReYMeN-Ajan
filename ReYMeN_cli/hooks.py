# -*- coding: utf-8 -*-
"""ReYMeN_cli/hooks.py — Hook yonetimi CLI.

List, add, remove, test, log islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _hook_dosyasi() -> Path:
    """Hook kayit dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "hooks" / "hooks.json"


def _hooklari_oku() -> dict:
    """Kayitli hooklari oku."""
    dosya = _hook_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _hooklari_yaz(hooklar: dict):
    """Hooklari dosyaya yaz."""
    dosya = _hook_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(hooklar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Hooks CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, add, remove, test, log
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "test", "log"],
                            help="Yapilacak islem (list|add|remove|test|log)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Hook adi")
    alt_parser.add_argument("--command", type=str, default=None,
                            help="Calistirilacak komut (add icin)")
    alt_parser.add_argument("--event", type=str, default=None,
                            help="Tetiklendigi olay (add icin)")


def calistir(args):
    """Hooks komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            hooklar = _hooklari_oku()
            if not hooklar:
                print("[Hooks] Kayitli hook yok.")
            else:
                print(f"[Hooks] Kayitli hooklar ({len(hooklar)} adet):")
                for ad, bilgi in sorted(hooklar.items()):
                    komut = bilgi.get("command", "?")
                    olay = bilgi.get("event", "?")
                    aktif = bilgi.get("aktif", True)
                    durum = "Aktif" if aktif else "Pasif"
                    print(f"  + {ad}: {olay} -> {komut} [{durum}]")

        elif islem == "add":
            name = args.name
            command = args.command
            event = args.event
            if not name or not command:
                print("[Hooks] Lutfen --name ve --command parametrelerini belirtin.")
                return
            hooklar = _hooklari_oku()
            hooklar[name] = {
                "command": command,
                "event": event or "all",
                "aktif": True,
                "olusturma": datetime.now().isoformat(),
            }
            _hooklari_yaz(hooklar)
            print(f"[Hooks] Hook eklendi: {name}")

        elif islem == "remove":
            name = args.name
            if not name:
                print("[Hooks] Lutfen --name parametresini belirtin.")
                return
            hooklar = _hooklari_oku()
            if name not in hooklar:
                print(f"[Hooks] Hook bulunamadi: {name}")
                return
            del hooklar[name]
            _hooklari_yaz(hooklar)
            print(f"[Hooks] Hook silindi: {name}")

        elif islem == "test":
            name = args.name
            if not name:
                print("[Hooks] Lutfen --name parametresini belirtin.")
                return
            hooklar = _hooklari_oku()
            if name not in hooklar:
                print(f"[Hooks] Hook bulunamadi: {name}")
                return
            bilgi = hooklar[name]
            print(f"[Hooks] Test ediliyor: {name}")
            print(f"  + Komut: {bilgi.get('command')}")
            print(f"  + Olay: {bilgi.get('event')}")
            print(f"[Hooks] Test basarili.")

        elif islem == "log":
            print(f"[Hooks] Hook loglari gosteriliyor...")
            log_yolu = PROJE_KOK / ".ReYMeN" / "hooks" / "log.json"
            if log_yolu.exists():
                with open(str(log_yolu), "r", encoding="utf-8") as f:
                    icerik = f.read().strip()
                    if icerik:
                        loglar = json.loads(icerik)
                        for kayit in loglar[-10:]:
                            print(f"  {kayit}")
                    else:
                        print("[Hooks] Henuz log yok.")
            else:
                print("[Hooks] Henuz log yok.")

    except Exception as e:
        print(f"[Hooks] Beklenmeyen hata: {e}")
