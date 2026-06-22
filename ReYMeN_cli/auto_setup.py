# -*- coding: utf-8 -*-
"""ReYMeN_cli/auto_setup.py — Otomatik Kurulum CLI.

Ortam degiskenleri, bagimliliklar ve yapilandirmalarin
otomatik olarak algilanip kurulmasini saglar.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _python_kontrol() -> list[str]:
    """Python surum ve paket kontrolleri yapar."""
    sonuclar = []
    sonuclar.append(f"Python: {sys.version.split()[0]}")
    try:
        import pip
        sonuclar.append(f"pip: {pip.__version__}")
    except ImportError:
        sonuclar.append("pip: bulunamadi")
    return sonuclar


def _env_kontrol() -> list[str]:
    """Ortam degiskenlerini kontrol eder."""
    sonuclar = []
    gerekli = ["HOME", "PATH", "USER"]
    for degisken in gerekli:
        if os.environ.get(degisken):
            sonuclar.append(f"{degisken}: OK")
        else:
            sonuclar.append(f"{degisken}: EKSIK")
    return sonuclar


def _proje_kontrol() -> list[str]:
    """Proje yapisini kontrol eder."""
    sonuclar = []
    kritik_dizinler = ["gateway", "ReYMeN_cli", ".ReYMeN"]
    for dizin in kritik_dizinler:
        if (PROJE_KOK / dizin).exists():
            sonuclar.append(f"{dizin}/: OK")
        else:
            sonuclar.append(f"{dizin}/: EKSIK")
    return sonuclar


def kaydet(alt_parser):
    """auto_setup CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["check", "fix", "env", "deps", "all"],
                            help="Yapilacak islem (check|fix|env|deps|all)")
    alt_parser.add_argument("--force", action="store_true", help="Onay gerektirmeden uygula")
    alt_parser.add_argument("--python", type=str, default=sys.executable, help="Python yolu")


def calistir(args):
    """auto_setup komutunu calistir."""
    try:
        islem = args.islem or "check"
        print(f"[AutoSetup] Baslatiliyor: {islem}")

        if islem in ("check", "all"):
            print("\n--- Python Kontrol ---")
            for satir in _python_kontrol():
                print(f"  {satir}")
            print("\n--- Ortam Kontrol ---")
            for satir in _env_kontrol():
                print(f"  {satir}")
            print("\n--- Proje Kontrol ---")
            for satir in _proje_kontrol():
                print(f"  {satir}")

        if islem in ("env", "all"):
            env_yolu = PROJE_KOK / ".env"
            if not env_yolu.exists():
                ornek = PROJE_KOK / ".env.example"
                if ornek.exists():
                    import shutil
                    shutil.copy2(str(ornek), str(env_yolu))
                    print(f"[AutoSetup] .env olusturuldu (.env.example'dan)")
                else:
                    print("[AutoSetup] .env.example bulunamadi, .env olusturulamadi")
            else:
                print("[AutoSetup] .env zaten mevcut")

        if islem in ("deps", "all"):
            requirements = PROJE_KOK / "requirements.txt"
            if requirements.exists():
                print("[AutoSetup] Bagimliliklar kontrol ediliyor...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r",
                                str(requirements), "--quiet"], check=False)
                print("[AutoSetup] Bagimliliklar kontrol edildi")
            else:
                print("[AutoSetup] requirements.txt bulunamadi")

        if islem == "fix":
            print("[AutoSetup] Otomatik duzeltme baslatiliyor...")
            kritik_dizinler = ["logs", "backups", "data"]
            for dizin in kritik_dizinler:
                (PROJE_KOK / dizin).mkdir(exist_ok=True)
                print(f"[AutoSetup]  -> {dizin}/ olusturuldu")

        print(f"[AutoSetup] Tamamlandi: {islem}")

    except Exception as e:
        print(f"[AutoSetup] Hata: {e}")
