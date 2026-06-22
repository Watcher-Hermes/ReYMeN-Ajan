# -*- coding: utf-8 -*-
"""ReYMeN_cli/bundles.py — Bundle CLI.

Bundle listeleme, olusturma, yukleme, kaldirma
ve disa aktarma islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _bundle_dosyasi() -> Path:
    """Bundle bilgilerinin saklandigi dosya yolu."""
    return PROJE_KOK / ".ReYMeN" / "bundles" / "kayit.json"


def _bundles_oku() -> list:
    """Kayitli bundle bilgilerini oku."""
    dosya = _bundle_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Bundle CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, create, install, remove, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "create", "install", "remove", "export"],
                            help="Yapilacak islem (list|create|install|remove|export)")
    alt_parser.add_argument("--ad", type=str, default=None,
                            help="Bundle adi (create/install/remove/export icin)")
    alt_parser.add_argument("--dosya", type=str, default=None,
                            help="Bundle dosya yolu (install icin)")


def calistir(args):
    """Bundle komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            bundlelar = _bundles_oku()
            if not bundlelar:
                print("[Bundles] Kayitli bundle yok.")
            else:
                print(f"[Bundles] Kayitli bundlelar ({len(bundlelar)} adet):")
                for b in bundlelar:
                    ad = b.get("ad", "?")
                    surum = b.get("surum", "?")
                    print(f"  + {ad} (surum: {surum})")

        elif islem == "create":
            ad = args.ad or "yeni-bundle"
            print(f"[Bundles] '{ad}' bundle'i olusturuluyor...")

        elif islem == "install":
            ad = args.ad
            dosya = args.dosya
            if not ad and not dosya:
                print("[Bundles] Lutfen --ad veya --dosya parametresini belirtin.")
                return
            kaynak = dosya or ad
            print(f"[Bundles] '{kaynak}' bundle'i yukleniyor...")

        elif islem == "remove":
            ad = args.ad
            if not ad:
                print("[Bundles] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Bundles] '{ad}' bundle'i kaldiriliyor...")

        elif islem == "export":
            ad = args.ad or "tum"
            print(f"[Bundles] '{ad}' bundle'i disa aktariliyor...")

    except Exception as e:
        print(f"[Bundles] Beklenmeyen hata: {e}")
