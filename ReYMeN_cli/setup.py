# -*- coding: utf-8 -*-
"""ReYMeN_cli/setup.py — Kurulum CLI.

Check, fix, deps, config, test islemleri.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _gerekli_paketler() -> list:
    """Gerekli Python paket listesi."""
    return [
        "flask", "requests", "python-dotenv",
    ]


def _paket_kontrol(paket: str) -> bool:
    """Bir paketin yuklu olup olmadigini kontrol et."""
    try:
        __import__(paket)
        return True
    except ImportError:
        return False


def kaydet(alt_parser):
    """Setup CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: check, fix, deps, config, test
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["check", "fix", "deps", "config", "test"],
                            help="Yapilacak islem (check|fix|deps|config|test)")
    alt_parser.add_argument("--package", type=str, default=None,
                            help="Paket adi (deps icin)")


def calistir(args):
    """Setup komutunu calistir."""
    try:
        islem = args.islem or "check"

        if islem == "check":
            print("[Setup] Sistem kontrol ediliyor...")
            sorunlar = []

            py_ver = sys.version_info
            if py_ver.major < 3 or (py_ver.major == 3 and py_ver.minor < 10):
                sorunlar.append(f"Python 3.10+ gerekli, mevcut: {py_ver.major}.{py_ver.minor}")

            for p in _gerekli_paketler():
                if not _paket_kontrol(p):
                    sorunlar.append(f"Paket eksik: {p}")

            gerekli_dosyalar = ["main.py", "motor.py", "beyin.py"]
            for d in gerekli_dosyalar:
                if not (PROJE_KOK / d).exists():
                    sorunlar.append(f"Dosya eksik: {d}")

            if sorunlar:
                print(f"[Setup] {len(sorunlar)} sorun bulundu:")
                for s in sorunlar:
                    print(f"  ! {s}")
            else:
                print("[Setup] Her sey yolunda.")

        elif islem == "fix":
            print("[Setup] Sorunlar duzeltiliyor...")
            for p in _gerekli_paketler():
                if not _paket_kontrol(p):
                    print(f"  + Yukleniyor: {p}")
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", p])
                        print(f"  + {p} yuklendi.")
                    except Exception as ex:
                        print(f"  ! {p} yuklenemedi: {ex}")
            print("[Setup] Duzeltme tamam.")

        elif islem == "deps":
            package = args.package
            if package:
                if _paket_kontrol(package):
                    mod = __import__(package)
                    ver = getattr(mod, "__version__", "?")
                    print(f"[Setup] {package} {ver}")
                else:
                    print(f"[Setup] {package} yuklu degil.")
            else:
                print("[Setup] Bagimliliklar:")
                for p in _gerekli_paketler():
                    durum = "Mevcut" if _paket_kontrol(p) else "Eksik"
                    print(f"  + {p}: {durum}")

        elif islem == "config":
            print("[Setup] Yapilandirma kontrolu:")
            env_yolu = PROJE_KOK / ".env"
            if env_yolu.exists():
                print(f"  + .env dosyasi: Mevcut")
            else:
                print(f"  ! .env dosyasi: Bulunamadi")

            ReYMeN_dir = PROJE_KOK / ".ReYMeN"
            if ReYMeN_dir.exists():
                print(f"  + .ReYMeN klasoru: Mevcut")
            else:
                print(f"  ! .ReYMeN klasoru: Bulunamadi")

        elif islem == "test":
            print("[Setup] Kurulum test ediliyor...")
            testler = 0
            basarili = 0
            for p in _gerekli_paketler():
                testler += 1
                if _paket_kontrol(p):
                    basarili += 1
            print(f"[Setup] Test sonucu: {basarili}/{testler} basarili")
            if basarili == testler:
                print("[Setup] Kurulum tamam.")
            else:
                print("[Setup] Bazi paketler eksik. 'fix' komutunu calistirin.")

    except Exception as e:
        print(f"[Setup] Beklenmeyen hata: {e}")
