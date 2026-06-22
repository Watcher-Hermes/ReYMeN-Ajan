# -*- coding: utf-8 -*-
"""ReYMeN_cli/doctor.py — Sistem teshisi CLI.

Sistem, araclar, gateway, hafiza ve ag saglik kontrolleri.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _env_oku(anahtar: str, varsayilan: str = "") -> str:
    """.env dosyasindan anahtar degerini oku."""
    env_yolu = PROJE_KOK / ".env"
    if not env_yolu.exists():
        return varsayilan
    with open(str(env_yolu), "r", encoding="utf-8") as f:
        for satir in f:
            satir_stripped = satir.strip()
            if satir_stripped.startswith("#") or "=" not in satir_stripped:
                continue
            k, v = satir_stripped.split("=", 1)
            if k.strip() == anahtar:
                return v.strip().strip('"').strip("'")
    return varsayilan


def _kontrol_et(etiket: str, durum: bool, basarili_mesaj: str, hata_mesaj: str) -> tuple:
    """Kontrol sonucunu dondur."""
    if durum:
        return (True, f"[OK] {etiket}: {basarili_mesaj}")
    else:
        return (False, f"[!] {etiket}: {hata_mesaj}")


def kaydet(alt_parser):
    """Doctor CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: all, tools, gateway, memory, network
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["all", "tools", "gateway", "memory", "network"],
                            help="Kontrol edilecek alan (all|tools|gateway|memory|network)")


def calistir(args):
    """Doctor komutunu calistir."""
    try:
        islem = args.islem or "all"

        if islem in ("all", "tools"):
            print(f"[Doctor] Arac kontrolleri:")
            araclar = [
                ("Python", sys.version.split()[0], sys.version_info >= (3, 10)),
                ("Git", "git" in str(subprocess.run(["which", "git"], capture_output=True, text=True).stdout) if sys.platform != "win32" else True, True),
            ]
            if sys.platform == "win32":
                git_check = subprocess.run(["where", "git"], capture_output=True, text=True)
                araclar[1] = ("Git", "Mevcut" if git_check.returncode == 0 else "Yok", git_check.returncode == 0)
            for ad, ver, durum in araclar:
                if durum:
                    print(f"  + {ad}: {ver}")
                else:
                    print(f"  ! {ad}: {ver} (Eksik)")

            gerekli_dosyalar = ["main.py", "motor.py", "beyin.py", "setup.py"]
            eksik = [d for d in gerekli_dosyalar if not (PROJE_KOK / d).exists()]
            if eksik:
                print(f"  ! Eksik dosyalar: {', '.join(eksik)}")
            else:
                print(f"  + Temel moduller mevcut")

        if islem in ("all", "gateway"):
            print(f"\n[Doctor] Gateway kontrolleri:")
            token = _env_oku("TELEGRAM_BOT_TOKEN", "")
            chat_id = _env_oku("TELEGRAM_CHAT_ID", "")
            if token:
                print(f"  + Telegram Token: Mevcut")
            else:
                print(f"  ! Telegram Token: Ayarlanmamis")
            if chat_id:
                print(f"  + Telegram Chat ID: {chat_id}")
            else:
                print(f"  ! Telegram Chat ID: Ayarlanmamis")
            try:
                import flask
                print(f"  + Flask: Mevcut")
            except ImportError:
                print(f"  ! Flask: Yuklu degil")

        if islem in ("all", "memory"):
            print(f"\n[Doctor] Hafiza kontrolleri:")
            mem_dir = PROJE_KOK / ".ReYMeN" / "memories"
            if mem_dir.exists():
                toplam = sum(f.stat().st_size for f in mem_dir.iterdir() if f.is_file())
                print(f"  + Hafiza klasoru: {mem_dir}")
                print(f"  + Toplam boyut: {toplam} B")
            else:
                print(f"  ! Hafiza klasoru bulunamadi")

        if islem in ("all", "network"):
            print(f"\n[Doctor] Ag kontrolleri:")
            lm_url = _env_oku("LMSTUDIO_BASE_URL", "")
            if lm_url:
                import urllib.request
                try:
                    urllib.request.urlopen(lm_url, timeout=5)
                    print(f"  + LM Studio ulasilabilir: {lm_url}")
                except Exception:
                    print(f"  ! LM Studio ulasilamadi: {lm_url}")
            else:
                print(f"  ! LMSTUDIO_BASE_URL ayarlanmamis")
            try:
                import socket
                socket.gethostbyname("google.com")
                print(f"  + Internet baglantisi: Var")
            except Exception:
                print(f"  ! Internet baglantisi: Yok")

        if islem == "all":
            print(f"\n[Doctor] Sistem ozeti:")
            py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            print(f"  Platform: {sys.platform}")
            print(f"  Python: {py_ver}")
            print(f"  Proje: {PROJE_KOK}")
            try:
                toplam, kullanilan, bos = shutil.disk_usage(str(PROJE_KOK))
                print(f"  Disk: {bos / (1024**3):.1f} GB bos")
            except Exception:
                pass

    except Exception as e:
        print(f"[Doctor] Beklenmeyen hata: {e}")
