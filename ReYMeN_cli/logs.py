# -*- coding: utf-8 -*-
"""ReYMeN_cli/logs.py — Log goruntuleyici CLI.

Tail, search, level, export, clear islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _log_dosyasi() -> Path:
    """Ana log dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "logs" / "ReYMeN.log"


def _log_ayar_dosyasi() -> Path:
    """Log ayar dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "logs" / "settings.json"


def _log_ayarlarini_oku() -> dict:
    """Log ayarlarini oku."""
    dosya = _log_ayar_dosyasi()
    if not dosya.exists():
        return {"seviye": "INFO", "maks_boyut": 10485760}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"seviye": "INFO", "maks_boyut": 10485760}
    except (json.JSONDecodeError, Exception):
        return {"seviye": "INFO", "maks_boyut": 10485760}


def _log_ayarlarini_yaz(ayarlar: dict):
    """Log ayarlarini yaz."""
    dosya = _log_ayar_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(ayarlar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Logs CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: tail, search, level, export, clear
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["tail", "search", "level", "export", "clear"],
                            help="Yapilacak islem (tail|search|level|export|clear)")
    alt_parser.add_argument("--lines", type=int, default=20,
                            help="Gosterilecek satir sayisi (tail icin)")
    alt_parser.add_argument("--query", type=str, default=None,
                            help="Arama metni (search icin)")
    alt_parser.add_argument("--level", type=str, default=None,
                            help="Log seviyesi (DEBUG|INFO|WARNING|ERROR)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (export icin)")


def calistir(args):
    """Logs komutunu calistir."""
    try:
        islem = args.islem or "tail"

        if islem == "tail":
            lines = args.lines or 20
            log_dosya = _log_dosyasi()
            if not log_dosya.exists():
                print("[Logs] Log dosyasi bulunamadi.")
                return
            with open(str(log_dosya), "r", encoding="utf-8") as f:
                satirlar = f.readlines()
            son_satirlar = satirlar[-lines:]
            print(f"[Logs] Son {len(son_satirlar)} satir:")
            for satir in son_satirlar:
                print(satir.rstrip())

        elif islem == "search":
            query = args.query
            if not query:
                print("[Logs] Lutfen --query parametresini belirtin.")
                return
            log_dosya = _log_dosyasi()
            if not log_dosya.exists():
                print("[Logs] Log dosyasi bulunamadi.")
                return
            with open(str(log_dosya), "r", encoding="utf-8") as f:
                satirlar = f.readlines()
            eslesenler = [s for s in satirlar if query.lower() in s.lower()]
            print(f"[Logs] '{query}' icin {len(eslesenler)} eslesme:")
            for satir in eslesenler[-20:]:
                print(satir.rstrip())

        elif islem == "level":
            level = args.level
            if level:
                ayarlar = _log_ayarlarini_oku()
                ayarlar["seviye"] = level.upper()
                _log_ayarlarini_yaz(ayarlar)
                print(f"[Logs] Log seviyesi: {level.upper()}")
            else:
                ayarlar = _log_ayarlarini_oku()
                print(f"[Logs] Mevcut log seviyesi: {ayarlar.get('seviye', 'INFO')}")

        elif islem == "export":
            output = args.output or str(PROJE_KOK / ".ReYMeN" / "logs" / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
            log_dosya = _log_dosyasi()
            if not log_dosya.exists():
                print("[Logs] Log dosyasi bulunamadi.")
                return
            import shutil
            shutil.copy2(str(log_dosya), output)
            print(f"[Logs] Log export edildi: {output}")

        elif islem == "clear":
            log_dosya = _log_dosyasi()
            log_dosya.parent.mkdir(parents=True, exist_ok=True)
            with open(str(log_dosya), "w", encoding="utf-8") as f:
                f.write("")
            print("[Logs] Log dosyasi temizlendi.")

    except Exception as e:
        print(f"[Logs] Beklenmeyen hata: {e}")
