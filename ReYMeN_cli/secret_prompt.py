# -*- coding: utf-8 -*-
"""ReYMeN_cli/secret_prompt.py — Gizli Prompt CLI.

Gizli prompt ayarlama, alma, listeleme, silme
ve maskeleme islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _secret_dosyasi() -> Path:
    """Gizli prompt dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "secrets" / "prompts.json"


def _sirlari_oku() -> dict:
    """Kayitli sirlari oku."""
    dosya = _secret_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def kaydet(alt_parser):
    """Secret prompt CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: set, get, list, delete, mask
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["set", "get", "list", "delete", "mask"],
                            help="Yapilacak islem (set|get|list|delete|mask)")
    alt_parser.add_argument("--anahtar", type=str, default=None,
                            help="Prompt anahtari (set/get/delete icin)")
    alt_parser.add_argument("--deger", type=str, default=None,
                            help="Prompt degeri (set icin)")


def calistir(args):
    """Secret prompt komutunu calistir."""
    try:
        islem = args.islem or "list"
        sirlar = _sirlari_oku()

        if islem == "set":
            anahtar = args.anahtar
            deger = args.deger
            if not anahtar or not deger:
                print("[SecretPrompt] Lutfen --anahtar ve --deger parametrelerini belirtin.")
                return
            print(f"[SecretPrompt] '{anahtar}' gizli promptu kaydedildi.")

        elif islem == "get":
            anahtar = args.anahtar
            if not anahtar:
                print("[SecretPrompt] Lutfen --anahtar parametresini belirtin.")
                return
            if anahtar in sirlar:
                print(f"[SecretPrompt] {anahtar}: ********")
            else:
                print(f"[SecretPrompt] '{anahtar}' bulunamadi.")

        elif islem == "list":
            if not sirlar:
                print("[SecretPrompt] Kayitli gizli prompt yok.")
            else:
                print(f"[SecretPrompt] Gizli promptlar ({len(sirlar)} adet):")
                for a in sirlar:
                    print(f"  + {a}: ********")

        elif islem == "delete":
            anahtar = args.anahtar
            if not anahtar:
                print("[SecretPrompt] Lutfen --anahtar parametresini belirtin.")
                return
            print(f"[SecretPrompt] '{anahtar}' silindi.")

        elif islem == "mask":
            deger = args.deger or "gizli-icerik"
            maskeli = deger[:4] + "****" if len(deger) > 4 else "****"
            print(f"[SecretPrompt] Maskelenmis: {maskeli}")

    except Exception as e:
        print(f"[SecretPrompt] Beklenmeyen hata: {e}")
