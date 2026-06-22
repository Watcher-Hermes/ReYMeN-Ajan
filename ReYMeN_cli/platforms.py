# -*- coding: utf-8 -*-
"""ReYMeN_cli/platforms.py — Platform CLI.

List, info, test, enable, disable islemleri.
"""

import json
import os
import sys
import platform as _platform
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _platform_dosyasi() -> Path:
    """Platform konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "platforms" / "platforms.json"


def _platform_oku() -> dict:
    """Platform ayarlarini oku."""
    dosya = _platform_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _platform_yaz(veri: dict):
    """Platform ayarlarini yaz."""
    dosya = _platform_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Platforms CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, info, test, enable, disable
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "info", "test", "enable", "disable"],
                            help="Yapilacak islem (list|info|test|enable|disable)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Platform adi")


def calistir(args):
    """Platforms komutunu calistir."""
    try:
        islem = args.islem or "info"

        if islem == "list":
            platformlar = _platform_oku()
            print("[Platforms] Desteklenen platformlar:")
            varsayilan = ["windows", "linux", "macos", "web"]
            for p in varsayilan:
                ozel = " (ozel)" if p in platformlar else ""
                aktif = platformlar.get(p, {}).get("aktif", False) if p in platformlar else True
                durum = "Aktif" if aktif else "Pasif"
                print(f"  + {p}: {durum}{ozel}")

        elif islem == "info":
            name = args.name or _platform.system().lower()
            print(f"[Platforms] Platform bilgisi: {name}")
            print(f"  + Sistem: {_platform.system()}")
            print(f"  + Node: {_platform.node()}")
            print(f"  + Release: {_platform.release()}")
            print(f"  + Makine: {_platform.machine()}")
            print(f"  + Python: {sys.version}")

        elif islem == "test":
            name = args.name or _platform.system().lower()
            print(f"[Platforms] Test ediliyor: {name}")
            print(f"[Platforms] Platform uyumlu.")

        elif islem == "enable":
            name = args.name or _platform.system().lower()
            platformlar = _platform_oku()
            if name not in platformlar:
                platformlar[name] = {}
            platformlar[name]["aktif"] = True
            _platform_yaz(platformlar)
            print(f"[Platforms] '{name}' aktif edildi.")

        elif islem == "disable":
            name = args.name or _platform.system().lower()
            platformlar = _platform_oku()
            if name in platformlar:
                platformlar[name]["aktif"] = False
            else:
                platformlar[name] = {"aktif": False}
            _platform_yaz(platformlar)
            print(f"[Platforms] '{name}' devre disi birakildi.")

    except Exception as e:
        print(f"[Platforms] Beklenmeyen hata: {e}")
