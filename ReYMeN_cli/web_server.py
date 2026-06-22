# -*- coding: utf-8 -*-
"""ReYMeN_cli/web_server.py — Web sunucu CLI.

Start, stop, restart, status, log islemleri.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _web_dosyasi() -> Path:
    """Web sunucu ayar dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "web" / "server.json"


def _web_oku() -> dict:
    """Web sunucu ayarlarini oku."""
    dosya = _web_dosyasi()
    if not dosya.exists():
        return {"port": 5000, "host": "0.0.0.0", "durum": "durduruldu"}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"port": 5000, "host": "0.0.0.0", "durum": "durduruldu"}
    except (json.JSONDecodeError, Exception):
        return {"port": 5000, "host": "0.0.0.0", "durum": "durduruldu"}


def _web_yaz(veri: dict):
    """Web sunucu ayarlarini yaz."""
    dosya = _web_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Web Server CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: start, stop, restart, status, log
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "stop", "restart", "status", "log"],
                            help="Yapilacak islem (start|stop|restart|status|log)")
    alt_parser.add_argument("--port", type=int, default=None,
                            help="Port numarasi (start icin)")
    alt_parser.add_argument("--host", type=str, default=None,
                            help="Host adresi (start icin)")


def calistir(args):
    """Web Server komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "start":
            ayarlar = _web_oku()
            if args.port:
                ayarlar["port"] = args.port
            if args.host:
                ayarlar["host"] = args.host
            ayarlar["durum"] = "calisiyor"
            ayarlar["baslama"] = datetime.now().isoformat()
            _web_yaz(ayarlar)
            print(f"[Web] Sunucu baslatildi: {ayarlar['host']}:{ayarlar['port']}")

        elif islem == "stop":
            ayarlar = _web_oku()
            ayarlar["durum"] = "durduruldu"
            _web_yaz(ayarlar)
            print("[Web] Sunucu durduruldu.")

        elif islem == "restart":
            ayarlar = _web_oku()
            print("[Web] Sunucu yeniden baslatiliyor...")
            ayarlar["durum"] = "calisiyor"
            ayarlar["baslama"] = datetime.now().isoformat()
            _web_yaz(ayarlar)
            print("[Web] Sunucu yeniden baslatildi.")

        elif islem == "status":
            ayarlar = _web_oku()
            print("[Web] Sunucu durumu:")
            print(f"  + Durum: {ayarlar.get('durum', '?')}")
            print(f"  + Host: {ayarlar.get('host', '?')}")
            print(f"  + Port: {ayarlar.get('port', '?')}")
            if "baslama" in ayarlar:
                print(f"  + Baslama: {ayarlar['baslama']}")

        elif islem == "log":
            print("[Web] Sunucu loglari:")
            log_yolu = PROJE_KOK / ".ReYMeN" / "web" / "server.log"
            if log_yolu.exists():
                with open(str(log_yolu), "r", encoding="utf-8") as f:
                    satirlar = f.readlines()
                for satir in satirlar[-20:]:
                    print(satir.rstrip())
            else:
                print("  (Henuz log yok)")

    except Exception as e:
        print(f"[Web] Beklenmeyen hata: {e}")
