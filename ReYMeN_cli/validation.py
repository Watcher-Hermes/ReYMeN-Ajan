# -*- coding: utf-8 -*-
"""ReYMeN_cli/validation.py — Dogrulama CLI.

Veri, yapilandirma ve dosya dogrulama islemleri.
"""

import json
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _json_dogrula(dosya_yolu: Path) -> tuple[bool, str]:
    """JSON dosyasini dogrular."""
    try:
        with open(str(dosya_yolu), "r", encoding="utf-8") as f:
            json.load(f)
        return True, "Gecerli JSON"
    except json.JSONDecodeError as e:
        return False, f"JSON hatasi: {e}"
    except Exception as e:
        return False, f"Dosya hatasi: {e}"


def _python_dogrula(dosya_yolu: Path) -> tuple[bool, str]:
    """Python dosyasini sentaks acisindan dogrular."""
    try:
        with open(str(dosya_yolu), "r", encoding="utf-8") as f:
            compile(f.read(), dosya_yolu.name, "exec")
        return True, "Gecerli Python"
    except SyntaxError as e:
        return False, f"Sentaks hatasi: {e}"
    except Exception as e:
        return False, f"Hata: {e}"


def kaydet(alt_parser):
    """validation CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["file", "config", "schema", "all", "format"],
                            help="Yapilacak islem (file|config|schema|all|format)")
    alt_parser.add_argument("--path", type=str, default=None, help="Dogrulanacak dosya")
    alt_parser.add_argument("--type", type=str, default="auto",
                            choices=["auto", "json", "python", "yaml"], help="Dosya turu")


def calistir(args):
    """validation komutunu calistir."""
    try:
        islem = args.islem or "config"
        print(f"[Validation] Baslatiliyor: {islem}")

        if islem == "file":
            dosya_yolu = Path(args.path) if args.path else __file__
            if not dosya_yolu.exists():
                print(f"[Validation] Dosya bulunamadi: {dosya_yolu}")
                return
            tur = args.type
            if tur == "auto":
                tur = "json" if dosya_yolu.suffix == ".json" else "python"

            if tur == "json":
                gecerli, mesaj = _json_dogrula(dosya_yolu)
            else:
                gecerli, mesaj = _python_dogrula(dosya_yolu)

            isaret = "OK" if gecerli else "HATA"
            print(f"[Validation] [{isaret}] {dosya_yolu.name}: {mesaj}")

        elif islem == "config":
            print("[Validation] Yapilandirma dogrulama:")
            for dosya in PROJE_KOK.rglob("*.json"):
                if "__pycache__" not in str(dosya):
                    gecerli, mesaj = _json_dogrula(dosya)
                    isaret = "OK" if gecerli else "HATA"
                    print(f"  [{isaret}] {dosya.relative_to(PROJE_KOK)}")

        elif islem == "schema":
            print("[Validation] Sema dogrulama (simule):")
            print("  [OK] gateway yapisi uygun")
            print("  [OK] ReYMeN_cli yapisi uygun")

        elif islem == "all":
            print("[Validation] Tum dosyalar dogrulaniyor...")
            hata = 0
            for dosya in PROJE_KOK.rglob("*.py"):
                if "__pycache__" not in str(dosya):
                    gecerli, _ = _python_dogrula(dosya)
                    if not gecerli:
                        hata += 1
                        print(f"  [HATA] {dosya.name}")
            print(f"  Tamamlandi: {hata} hata bulundu")

        elif islem == "format":
            print("[Validation] Format kontrolu (simule):")
            print("  [OK] Tum dosyalar uygun formatta")

    except Exception as e:
        print(f"[Validation] Hata: {e}")
