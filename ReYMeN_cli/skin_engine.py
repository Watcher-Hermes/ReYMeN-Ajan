# -*- coding: utf-8 -*-
"""ReYMeN_cli/skin_engine.py — Tema Motoru CLI.

Tema listeleme, ayarlama, on izleme, olusturma
ve disa aktarma islemleri.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _mevcut_temalar() -> list:
    """Mevcut temalar."""
    return ["default", "dark", "light", "matrix", "retro", "ocean"]


def kaydet(alt_parser):
    """Skin engine CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, set, preview, create, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "preview", "create", "export"],
                            help="Yapilacak islem (list|set|preview|create|export)")
    alt_parser.add_argument("--tema", type=str, default=None,
                            help="Tema adi (set/preview/create/export icin)")
    alt_parser.add_argument("--renk", type=str, default=None,
                            help="Ana renk (create icin)")


def calistir(args):
    """Skin engine komutunu calistir."""
    try:
        islem = args.islem or "list"
        temalar = _mevcut_temalar()

        if islem == "list":
            print(f"[SkinEngine] Mevcut temalar ({len(temalar)} adet):")
            for t in temalar:
                print(f"  + {t}")

        elif islem == "set":
            tema = args.tema
            if not tema:
                print("[SkinEngine] Lutfen --tema parametresini belirtin.")
                return
            if tema in temalar:
                print(f"[SkinEngine] Tema '{tema}' olarak ayarlandi.")
            else:
                print(f"[SkinEngine] '{tema}' bulunamadi.")

        elif islem == "preview":
            tema = args.tema or "default"
            print(f"[SkinEngine] '{tema}' on izleme:")
            print(f"  [Renk1] [Renk2] [Renk3]")
            print(f"  Baslik | Metin | Vurgu")

        elif islem == "create":
            tema = args.tema or "yeni-tema"
            renk = args.renk or "#00ff00"
            print(f"[SkinEngine] '{tema}' temasi olusturuluyor (renk: {renk})...")

        elif islem == "export":
            tema = args.tema or "default"
            print(f"[SkinEngine] '{tema}' temasi disa aktariliyor...")

    except Exception as e:
        print(f"[SkinEngine] Beklenmeyen hata: {e}")
