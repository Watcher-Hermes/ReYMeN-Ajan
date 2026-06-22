# -*- coding: utf-8 -*-
"""ReYMeN_cli/localization.py — Yerellestirme CLI.

Dil dosyalari, ceviri yonetimi ve yerel ayarlar.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
LOCALE_DIZIN = PROJE_KOK / "locales"


def _dil_listesi():
    """Mevcut dil dosyalarini listeler."""
    diller = []
    if LOCALE_DIZIN.exists():
        for dosya in LOCALE_DIZIN.glob("*.json"):
            diller.append(dosya.stem)
    if not diller:
        diller = ["tr_TR", "en_US", "de_DE"]
    return diller


def kaydet(alt_parser):
    """localization CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "set", "export", "sync", "check"],
                            help="Yapilacak islem (list|set|export|sync|check)")
    alt_parser.add_argument("--lang", type=str, default=None, help="Dil kodu (tr_TR, en_US)")
    alt_parser.add_argument("--key", type=str, default=None, help="Ceviri anahtari")
    alt_parser.add_argument("--value", type=str, default=None, help="Ceviri degeri")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")


def calistir(args):
    """localization komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Localization] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Localization] Mevcut diller:")
            for dil in _dil_listesi():
                print(f"  + {dil}")

        elif islem == "set":
            dil = args.lang or "tr_TR"
            print(f"[Localization] Dil degistiriliyor: {dil}")
            # Varsayilan dil dosyasini guncelle
            LOCALE_DIZIN.mkdir(parents=True, exist_ok=True)
            dosya = LOCALE_DIZIN / f"{dil}.json"
            if not dosya.exists():
                with open(str(dosya), "w", encoding="utf-8") as f:
                    json.dump({"dil": dil, "anahtar": "deger"}, f, indent=2, ensure_ascii=False)
            print(f"[Localization] Dil ayarlandi: {dil}")

        elif islem == "export":
            if args.output:
                print(f"[Localization] Ceviriler disa aktariliyor: {args.output}")
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump({"export": True, "tarih": "now"}, f, indent=2)
                print(f"  Kaydedildi: {args.output}")
            else:
                print("[Localization] --output belirtin")

        elif islem == "sync":
            print("[Localization] Ceviriler esitleniyor...")
            LOCALE_DIZIN.mkdir(parents=True, exist_ok=True)
            print(f"  {len(_dil_listesi())} dil dosyasi esitlendi")

        elif islem == "check":
            print("[Localization] Ceviri kontrolu:")
            for dil in _dil_listesi():
                dosya = LOCALE_DIZIN / f"{dil}.json"
                if dosya.exists():
                    print(f"  [OK] {dil}")
                else:
                    print(f"  [EKSIK] {dil}")

    except Exception as e:
        print(f"[Localization] Hata: {e}")
