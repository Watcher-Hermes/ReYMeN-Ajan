# -*- coding: utf-8 -*-
"""ReYMeN_cli/components.py — Bilesen Listeleme CLI.

Sistem bilesenlerini, surumlerini ve bagimliliklarini gorme.
"""

import importlib
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _bilesen_tara():
    """Projedeki Python modullerini tara."""
    bilesenler = []
    for dizin in ["gateway", "ReYMeN_cli"]:
        klasor = PROJE_KOK / dizin
        if klasor.exists():
            for dosya in sorted(klasor.glob("*.py")):
                if dosya.name != "__init__.py":
                    bilesenler.append((dizin, dosya.stem))
    return bilesenler


def kaydet(alt_parser):
    """components CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "info", "deps", "tree", "versions"],
                            help="Yapilacak islem (list|info|deps|tree|versions)")
    alt_parser.add_argument("--name", type=str, default=None, help="Bilesen adi")
    alt_parser.add_argument("--depth", type=int, default=1, help="Derinlik (tree icin)")


def calistir(args):
    """components komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Components] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Components] Proje bilesenleri:")
            for kategori, ad in _bilesen_tara():
                print(f"  [{kategori}] {ad}")

        elif islem == "info":
            ad = args.name
            if not ad:
                print("[Components] --name belirtin")
                return
            print(f"[Components] Bilesen bilgisi: {ad}")
            try:
                mod = importlib.import_module(ad)
                print(f"  Dosya: {getattr(mod, '__file__', 'bilinmiyor')}")
                print(f"  Doc: {getattr(mod, '__doc__', 'yok')[:80] if getattr(mod, '__doc__', 'yok') else 'yok'}...")
            except ImportError:
                print(f"  Modul bulunamadi: {ad}")

        elif islem == "deps":
            print("[Components] Bagimliliklar:")
            with open(PROJE_KOK / "requirements.txt") as f:
                for satir in f:
                    satir = satir.strip()
                    if satir and not satir.startswith("#"):
                        print(f"  {satir}")

        elif islem == "tree":
            print("[Components] Bilesen agaci (simule):")
            print("  ReYMeN_projesi/")
            print("  +-- gateway/ (26 dosya)")
            print("  +-- ReYMeN_cli/ (85+ modul)")
            print("  +-- .ReYMeN/ (yapilandirma)")

        elif islem == "versions":
            import sys
            print(f"[Components] Surumler:")
            print(f"  Python: {sys.version}")
            print(f"  Platform: {sys.platform}")

    except Exception as e:
        print(f"[Components] Hata: {e}")
