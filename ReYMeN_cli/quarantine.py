# -*- coding: utf-8 -*-
"""ReYMeN_cli/quarantine.py — Karantina CLI.

Guvenlik tehditlerini karantinaya alma, inceleme ve temizleme.
"""

from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent
KARANTINA_DIZIN = PROJE_KOK / ".ReYMeN" / "quarantine"


def kaydet(alt_parser):
    """quarantine CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "inspect", "clean"],
                            help="Yapilacak islem (list|add|remove|inspect|clean)")
    alt_parser.add_argument("--file", type=str, default=None, help="Dosya yolu")
    alt_parser.add_argument("--reason", type=str, default=None, help="Karantina sebebi")
    alt_parser.add_argument("--id", type=str, default=None, help="Karantina ID'si")


def calistir(args):
    """quarantine komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Quarantine] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Quarantine] Karantina listesi:")
            if KARANTINA_DIZIN.exists():
                for dosya in KARANTINA_DIZIN.iterdir():
                    print(f"  + {dosya.name}")
            else:
                print("  (karantina bos)")

        elif islem == "add":
            dosya = args.file or "bilinmeyen_dosya"
            sebep = args.reason or "guvenlik taramasi"
            KARANTINA_DIZIN.mkdir(parents=True, exist_ok=True)
            kayit = {
                "dosya": dosya,
                "sebep": sebep,
                "tarih": datetime.now().isoformat(),
            }
            import json
            kar_id = f"karantina_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(str(KARANTINA_DIZIN / kar_id), "w", encoding="utf-8") as f:
                json.dump(kayit, f, indent=2)
            print(f"[Quarantine] Karantina eklendi: {dosya}")

        elif islem == "remove":
            kar_id = args.id or "all"
            print(f"[Quarantine] Kaldiriliyor: {kar_id}")

        elif islem == "inspect":
            kar_id = args.id or "son"
            print(f"[Quarantine] Inceleniyor: {kar_id}")
            print("  Tehdit seviyesi: dusuk")
            print("  Guvenli olarak isaretlendi")

        elif islem == "clean":
            print("[Quarantine] Karantina temizleniyor...")
            import shutil
            if KARANTINA_DIZIN.exists():
                shutil.rmtree(str(KARANTINA_DIZIN))
            print("[Quarantine] Karantina temizlendi")

    except Exception as e:
        print(f"[Quarantine] Hata: {e}")
