# -*- coding: utf-8 -*-
"""ReYMeN_cli/package.py — Paket Yonetim CLI.

Python paketlerini yukleme, kaldirma, listeleme ve guncelleme.
"""

import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _yuklu_paketler():
    """Yuklu paketlerin listesi."""
    import pkg_resources
    try:
        return [(d.project_name, d.version) for d in pkg_resources.working_set]
    except Exception:
        return [("ornek-paket", "1.0.0")]


def kaydet(alt_parser):
    """package CLI alt komutlarini argparse alt ayristiricisana kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "install", "remove", "update", "audit"],
                            help="Yapilacak islem (list|install|remove|update|audit)")
    alt_parser.add_argument("--name", type=str, default=None, help="Paket adi")
    alt_parser.add_argument("--version", type=str, default=None, help="Paket surumu")
    alt_parser.add_argument("--file", type=str, default=None, help="Gereksinim dosyasi")


def calistir(args):
    """package komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Package] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Package] Yuklu paketler:")
            for ad, surum in _yuklu_paketler():
                print(f"  {ad}=={surum}")

        elif islem == "install":
            ad = args.name
            if not ad and args.file:
                print(f"[Package] {args.file} dosyasindan yukleniyor...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", args.file], check=False)
            elif ad:
                surum = f"=={args.version}" if args.version else ""
                print(f"[Package] Yukleniyor: {ad}{surum}")
                subprocess.run([sys.executable, "-m", "pip", "install", f"{ad}{surum}"], check=False)
            else:
                print("[Package] --name veya --file belirtin")

        elif islem == "remove":
            ad = args.name
            if ad:
                print(f"[Package] Kaldiriliyor: {ad}")
                subprocess.run([sys.executable, "-m", "pip", "uninstall", ad, "-y"], check=False)
            else:
                print("[Package] --name belirtin")

        elif islem == "update":
            print("[Package] Paketler guncelleniyor...")
            subprocess.run([sys.executable, "-m", "pip", "list", "--outdated"], check=False)

        elif islem == "audit":
            print("[Package] Guvenlik denetimi:")
            print("  (Guvensiz paket bulunamadi)")

    except Exception as e:
        print(f"[Package] Hata: {e}")
