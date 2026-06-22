# -*- coding: utf-8 -*-
"""ReYMeN_cli/resources.py — Kaynak Yonetim CLI.

Sistem kaynaklarini (disk, bellek, CPU) izleme ve yonetme.
"""

import os
import time
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _disk_kullanimi():
    """Disk kullanim bilgisi."""
    try:
        if hasattr(os, 'statvfs'):
            st = os.statvfs(str(PROJE_KOK))
            toplam = st.f_frsize * st.f_blocks
            bos = st.f_frsize * st.f_bavail
            kullanilan = toplam - bos
            return toplam, kullanilan, bos
        return 0, 0, 0
    except Exception:
        return 0, 0, 0


def kaydet(alt_parser):
    """resources CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["disk", "memory", "cpu", "all", "limits"],
                            help="Yapilacak islem (disk|memory|cpu|all|limits)")
    alt_parser.add_argument("--watch", action="store_true", help="Canli izleme")


def calistir(args):
    """resources komutunu calistir."""
    try:
        islem = args.islem or "all"
        print(f"[Resources] Baslatiliyor: {islem}")

        if islem in ("disk", "all"):
            toplam, kullanilan, bos = _disk_kullanimi()
            print(f"\n--- Disk ---")
            if toplam > 0:
                print(f"  Toplam: {toplam / (1024**3):.1f} GB")
                print(f"  Kullanilan: {kullanilan / (1024**3):.1f} GB")
                print(f"  Bos: {bos / (1024**3):.1f} GB")
                print(f"  Kullanim: %{kullanilan / toplam * 100:.1f}")
            else:
                print("  Disk bilgisi alinamadi (Windows)")

        if islem in ("memory", "all"):
            print(f"\n--- Bellek ---")
            try:
                import psutil
                mem = psutil.virtual_memory()
                print(f"  Toplam: {mem.total / (1024**3):.1f} GB")
                print(f"  Kullanilan: {mem.used / (1024**3):.1f} GB")
                print(f"  Kullanim: %{mem.percent}")
            except ImportError:
                print("  psutil yuklu degil")

        if islem in ("cpu", "all"):
            print(f"\n--- CPU ---")
            try:
                import psutil
                print(f"  Kullanim: %{psutil.cpu_percent(interval=0.5)}")
                print(f"  Cekirdek: {psutil.cpu_count()}")
            except ImportError:
                print("  psutil yuklu degil")

        if islem == "limits":
            print("\n--- Kaynak Limitleri ---")
            print("  Disk: sinirsiz")
            print("  Bellek: sinirsiz")
            print("  CPU: sinirsiz")

    except Exception as e:
        print(f"[Resources] Hata: {e}")
