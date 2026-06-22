# -*- coding: utf-8 -*-
"""ReYMeN_cli/diagnostics.py — Teshis CLI.

Sistem sorunlarini tespit etme, analiz ve cozum onerileri.
"""

import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _dizin_kontrol():
    """Kritik dizinlerin varligini kontrol eder."""
    sorunlar = []
    for dizin in ["gateway", "ReYMeN_cli", ".ReYMeN", "logs"]:
        yol = PROJE_KOK / dizin
        if not yol.exists():
            sorunlar.append(f"Eksik dizin: {dizin}/")
    return sorunlar


def _baglanti_kontrol():
    """Temel baglantilari kontrol eder."""
    sorunlar = []
    if not sys.stdin.isatty():
        sorunlar.append("stdin terminal degil")
    return sorunlar


def kaydet(alt_parser):
    """diagnostics CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["run", "network", "disk", "memory", "all"],
                            help="Yapilacak islem (run|network|disk|memory|all)")
    alt_parser.add_argument("--output", type=str, default=None, help="Cikti dosyasi")
    alt_parser.add_argument("--verbose", action="store_true", help="Detayli cikti")


def calistir(args):
    """diagnostics komutunu calistir."""
    try:
        islem = args.islem or "run"
        print(f"[Diagnostics] Teshis baslatiliyor: {islem}")
        sonuclar = []

        if islem in ("run", "all"):
            print("\n--- Dizin Kontrol ---")
            for sorun in _dizin_kontrol():
                print(f"  ! {sorun}")
                sonuclar.append(sorun)

            print("\n--- Baglanti Kontrol ---")
            for sorun in _baglanti_kontrol():
                print(f"  ! {sorun}")
                sonuclar.append(sorun)

        if islem in ("network", "all"):
            print("\n--- Ag Kontrol ---")
            import socket
            try:
                socket.gethostbyname("localhost")
                print("  [OK] localhost cozulebiliyor")
            except Exception as e:
                print(f"  [HATA] DNS: {e}")
                sonuclar.append(f"Network: {e}")

        if islem in ("disk", "all"):
            print("\n--- Disk Kontrol ---")
            if hasattr(os, 'statvfs'):
                try:
                    st = os.statvfs(str(PROJE_KOK))
                    bos = st.f_frsize * st.f_bavail
                    print(f"  Bos alan: {bos / (1024**3):.1f} GB")
                except Exception as e:
                    print(f"  Disk bilgisi alinamadi: {e}")
            else:
                print("  Disk bilgisi: Windows platformu")

        if islem in ("memory", "all"):
            print("\n--- Bellek Kontrol ---")
            try:
                import psutil
                mem = psutil.virtual_memory()
                print(f"  Toplam: {mem.total / (1024**3):.1f} GB")
                print(f"  Kullanilan: {mem.used / (1024**3):.1f} GB")
                print(f"  Yuzde: {mem.percent}%")
            except ImportError:
                print("  psutil yuklu degil, basit kontrol...")
                print(f"  Python: {sys.version}")

        if sonuclar:
            print(f"\n[Diagnostics] Toplam {len(sonuclar)} sorun bulundu")
        else:
            print("\n[Diagnostics] Sorun bulunamadi")

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                for s in sonuclar:
                    f.write(f"{s}\n")
            print(f"[Diagnostics] Sonuc kaydedildi: {args.output}")

    except Exception as e:
        print(f"[Diagnostics] Hata: {e}")
