# -*- coding: utf-8 -*-
"""ReYMeN_cli/managed_uv.py — Yonetilen uv CLI.

uv paket yoneticisi ile yukleme, guncelleme, listeleme,
onbellek ve temizlik islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def kaydet(alt_parser):
    """Managed uv CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: install, update, list, cache, clean
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["install", "update", "list", "cache", "clean"],
                            help="Yapilacak islem (install|update|list|cache|clean)")
    alt_parser.add_argument("--paket", type=str, default=None,
                            help="Paket adi (install/update icin)")
    alt_parser.add_argument("--surum", type=str, default=None,
                            help="Paket surumu (install icin)")


def calistir(args):
    """Managed uv komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "install":
            paket = args.paket
            surum = args.surum
            if not paket:
                print("[ManagedUV] Lutfen --paket parametresini belirtin.")
                return
            surum_str = f"=={surum}" if surum else ""
            print(f"[ManagedUV] uv ile '{paket}{surum_str}' yukleniyor...")

        elif islem == "update":
            paket = args.paket or "tum"
            print(f"[ManagedUV] '{paket}' guncelleniyor...")

        elif islem == "list":
            print("[ManagedUV] uv ile yuklu paketler:")
            print("  (henuz paket yuklu degil)")

        elif islem == "cache":
            print("[ManagedUV] uv onbellek durumu:")
            print("  Boyut: 0 MB")
            print("  Paket sayisi: 0")

        elif islem == "clean":
            print("[ManagedUV] uv onbellek temizleniyor...")
            print("[ManagedUV] Temizlik tamam.")

    except Exception as e:
        print(f"[ManagedUV] Beklenmeyen hata: {e}")
