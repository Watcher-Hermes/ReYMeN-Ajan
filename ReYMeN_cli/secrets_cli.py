# -*- coding: utf-8 -*-
"""ReYMeN_cli/secrets_cli.py — Sir yonetimi CLI.

Set, get, list, delete, import islemleri.
"""

import json
import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _sir_dosyasi() -> Path:
    """Sir dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "secrets" / "secrets.json"


def _sirlari_oku() -> dict:
    """Kayitli sirlari oku."""
    dosya = _sir_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _sirlari_yaz(sirlar: dict):
    """Sirlari dosyaya yaz."""
    dosya = _sir_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(sirlar, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Secrets CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: set, get, list, delete, import
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["set", "get", "list", "delete", "import"],
                            help="Yapilacak islem (set|get|list|delete|import)")
    alt_parser.add_argument("--key", type=str, default=None,
                            help="Anahtar adi")
    alt_parser.add_argument("--value", type=str, default=None,
                            help="Deger (set icin)")
    alt_parser.add_argument("--file", type=str, default=None,
                            help="Dosya yolu (import icin)")


def calistir(args):
    """Secrets komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "set":
            key = args.key
            value = args.value
            if not key or not value:
                print("[Secrets] Lutfen --key ve --value parametrelerini belirtin.")
                return
            sirlar = _sirlari_oku()
            sirlar[key] = value
            _sirlari_yaz(sirlar)
            print(f"[Secrets] '{key}' kaydedildi.")

        elif islem == "get":
            key = args.key
            if not key:
                print("[Secrets] Lutfen --key parametresini belirtin.")
                return
            sirlar = _sirlari_oku()
            if key not in sirlar:
                print(f"[Secrets] Anahtar bulunamadi: {key}")
                return
            gizli = sirlar[key][:4] + "****" if len(sirlar[key]) > 4 else "****"
            print(f"[Secrets] {key}: {gizli}")

        elif islem == "list":
            sirlar = _sirlari_oku()
            if not sirlar:
                print("[Secrets] Kayitli sir yok.")
            else:
                print(f"[Secrets] Kayitli sirlar ({len(sirlar)} adet):")
                for k in sorted(sirlar.keys()):
                    print(f"  + {k}: ****")

        elif islem == "delete":
            key = args.key
            if not key:
                print("[Secrets] Lutfen --key parametresini belirtin.")
                return
            sirlar = _sirlari_oku()
            if key not in sirlar:
                print(f"[Secrets] Anahtar bulunamadi: {key}")
                return
            del sirlar[key]
            _sirlari_yaz(sirlar)
            print(f"[Secrets] '{key}' silindi.")

        elif islem == "import":
            dosya = args.file
            if not dosya:
                print("[Secrets] Lutfen --file parametresini belirtin.")
                return
            dosya_yolu = Path(dosya)
            if not dosya_yolu.exists():
                print(f"[Secrets] Dosya bulunamadi: {dosya}")
                return
            try:
                with open(str(dosya_yolu), "r", encoding="utf-8") as f:
                    yeni_sirlar = json.loads(f.read())
                sirlar = _sirlari_oku()
                sirlar.update(yeni_sirlar)
                _sirlari_yaz(sirlar)
                print(f"[Secrets] {len(yeni_sirlar)} adet sir import edildi.")
            except (json.JSONDecodeError, Exception) as ex:
                print(f"[Secrets] Import hatasi: {ex}")

    except Exception as e:
        print(f"[Secrets] Beklenmeyen hata: {e}")
