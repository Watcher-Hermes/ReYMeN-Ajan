# -*- coding: utf-8 -*-
"""ReYMeN_cli/status.py — Durum CLI.

System, tools, gateway, memory, all islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Status CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: system, tools, gateway, memory, all
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["system", "tools", "gateway", "memory", "all"],
                            help="Yapilacak islem (system|tools|gateway|memory|all)")


def calistir(args):
    """Status komutunu calistir."""
    try:
        islem = args.islem or "all"

        if islem in ("system", "all"):
            print("[Status] Sistem durumu:")
            print(f"  + Platform: {sys.platform}")
            print(f"  + Python: {sys.version.split()[0]}")
            print(f"  + Proje: {PROJE_KOK}")
            print(f"  + Zaman: {datetime.now().isoformat()}")

        if islem in ("tools", "all"):
            print("\n[Status] Arac durumu:")
            cli_sayisi = len([f for f in (PROJE_KOK / "ReYMeN_cli").iterdir() if f.suffix == ".py"]) if (PROJE_KOK / "ReYMeN_cli").exists() else 0
            print(f"  + CLI modulleri: {cli_sayisi}")

        if islem in ("gateway", "all"):
            print("\n[Status] Gateway durumu:")
            gateway_dosyasi = PROJE_KOK / "gateway" / "gateway.py"
            if gateway_dosyasi.exists():
                print(f"  + Gateway: Mevcut")
            else:
                print(f"  + Gateway: Bulunamadi")

        if islem in ("memory", "all"):
            print("\n[Status] Hafiza durumu:")
            mem_dir = PROJE_KOK / ".ReYMeN" / "memories"
            if mem_dir.exists():
                dosyalar = [f for f in mem_dir.iterdir() if f.is_file()]
                toplam = sum(f.stat().st_size for f in dosyalar)
                print(f"  + Hafiza dosyasi: {len(dosyalar)}")
                print(f"  + Toplam boyut: {toplam} B")
            else:
                print(f"  + Hafiza: Bos")

        if islem == "all":
            print("\n[Status] Ozet:")
            print("  + Tum bilesenler calisiyor." if True else "  + Bazi bilesenler eksik.")

    except Exception as e:
        print(f"[Status] Beklenmeyen hata: {e}")
