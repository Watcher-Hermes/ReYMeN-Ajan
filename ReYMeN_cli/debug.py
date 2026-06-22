# -*- coding: utf-8 -*-
"""ReYMeN_cli/debug.py — Debug CLI.

Log_level, trace, inspect, dump, profile islemleri.
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _debug_dosyasi() -> Path:
    """Debug ayar dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "debug" / "settings.json"


def _debug_oku() -> dict:
    """Debug ayarlarini oku."""
    dosya = _debug_dosyasi()
    if not dosya.exists():
        return {"log_seviye": "INFO", "trace_aktif": False}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"log_seviye": "INFO", "trace_aktif": False}
    except (json.JSONDecodeError, Exception):
        return {"log_seviye": "INFO", "trace_aktif": False}


def _debug_yaz(veri: dict):
    """Debug ayarlarini yaz."""
    dosya = _debug_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Debug CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: log_level, trace, inspect, dump, profile
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["log_level", "trace", "inspect", "dump", "profile"],
                            help="Yapilacak islem (log_level|trace|inspect|dump|profile)")
    alt_parser.add_argument("--level", type=str, default=None,
                            help="Log seviyesi (DEBUG|INFO|WARNING|ERROR)")
    alt_parser.add_argument("--target", type=str, default=None,
                            help="Hedef modul/dosya")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (dump icin)")


def calistir(args):
    """Debug komutunu calistir."""
    try:
        islem = args.islem or "log_level"

        if islem == "log_level":
            level = args.level
            if level:
                ayarlar = _debug_oku()
                ayarlar["log_seviye"] = level.upper()
                _debug_yaz(ayarlar)
                print(f"[Debug] Log seviyesi: {level.upper()}")
            else:
                ayarlar = _debug_oku()
                print(f"[Debug] Mevcut log seviyesi: {ayarlar.get('log_seviye', 'INFO')}")

        elif islem == "trace":
            ayarlar = _debug_oku()
            aktif = ayarlar.get("trace_aktif", False)
            if aktif:
                ayarlar["trace_aktif"] = False
                _debug_yaz(ayarlar)
                print("[Debug] Trace devre disi.")
            else:
                ayarlar["trace_aktif"] = True
                _debug_yaz(ayarlar)
                print("[Debug] Trace aktif.")

        elif islem == "inspect":
            target = args.target or "ReYMeN_cli"
            print(f"[Debug] Inspekt ediliyor: {target}")
            try:
                mod = __import__(target)
                print(f"  + Modul: {target}")
                print(f"  + Konum: {getattr(mod, '__file__', '?')}")
                uyeler = [x for x in dir(mod) if not x.startswith("_")]
                print(f"  + Uyeler ({len(uyeler)}): {', '.join(uyeler[:20])}")
            except ImportError:
                print(f"  ! Modul bulunamadi: {target}")

        elif islem == "dump":
            output = args.output or str(PROJE_KOK / ".ReYMeN" / "debug" / f"dump_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            veri = {
                "zaman": datetime.now().isoformat(),
                "python": sys.version,
                "platform": sys.platform,
                "proje": str(PROJE_KOK),
                "ayarlar": _debug_oku(),
            }
            with open(output, "w", encoding="utf-8") as f:
                json.dump(veri, f, indent=2, ensure_ascii=False)
            print(f"[Debug] Dump kaydedildi: {output}")

        elif islem == "profile":
            print("[Debug] Profil olculeri:")
            basla = time.time()
            sayac = 0
            for _ in range(100000):
                sayac += 1
            gecen = time.time() - basla
            print(f"  + 100000 iterasyon: {gecen:.4f}s")
            print(f"  + Modul sayisi: {len(sys.modules)}")

    except Exception as e:
        print(f"[Debug] Beklenmeyen hata: {e}")
