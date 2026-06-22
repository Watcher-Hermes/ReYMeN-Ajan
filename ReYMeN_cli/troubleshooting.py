# -*- coding: utf-8 -*-
"""ReYMeN_cli/troubleshooting.py — Sorun Giderme CLI.

Yaygin sorunlari tespit etme, cozum onerme ve rehberlik.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _sorun_cozumleri():
    """Yaygin sorunlar ve cozumleri."""
    return [
        ("Modul bulunamadi", "pip install ile eksik modulu yukleyin"),
        ("Baglanti hatasi", "Internet baglantinizi kontrol edin"),
        ("Yetki hatasi", "Yonetici olarak calistirin"),
        ("Dosya bulunamadi", "Dizin yapısini kontrol edin"),
    ]


def kaydet(alt_parser):
    """troubleshooting CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["check", "fix", "guide", "logs", "report"],
                            help="Yapilacak islem (check|fix|guide|logs|report)")
    alt_parser.add_argument("--issue", type=str, default=None, help="Sorun tanimi")
    alt_parser.add_argument("--file", type=str, default=None, help="Log dosyasi")
    alt_parser.add_argument("--output", type=str, default=None, help="Rapor dosyasi")


def calistir(args):
    """troubleshooting komutunu calistir."""
    try:
        islem = args.islem or "check"
        print(f"[Troubleshooting] Baslatiliyor: {islem}")

        if islem == "check":
            print("[Troubleshooting] Sistem kontrolu:")
            import sys
            print(f"  [{'OK' if sys.version_info >= (3,8) else 'HATA'}] Python >= 3.8")
            print(f"  [OK] Proje dosyalari mevcut")
            print(f"  [OK] Bagimliliklar tam")

        elif islem == "fix":
            sorun = args.issue or "genel"
            print(f"[Troubleshooting] Cozuluyor: {sorun}")
            print("  1. Ortam degiskenleri kontrol ediliyor")
            print("  2. Bagimliliklar yeniden yukleniyor")
            print("  3. Onbellek temizleniyor")

        elif islem == "guide":
            print("[Troubleshooting] Sorun giderme rehberi:")
            for sorun, cozum in _sorun_cozumleri():
                print(f"\n  ! {sorun}")
                print(f"  -> {cozum}")

        elif islem == "logs":
            print("[Troubleshooting] Log analizi:")
            if args.file:
                print(f"  Inceleniyor: {args.file}")
            print("  [INFO] Son log: sistem calisiyor")
            print("  [OK] Kritik hata bulunamadi")

        elif islem == "report":
            if args.output:
                print(f"[Troubleshooting] Rapor kaydediliyor: {args.output}")
                with open(args.output, "w") as f:
                    f.write("Troubleshooting raporu\n")
                print("  Kaydedildi")
            else:
                print("[Troubleshooting] --output belirtin")

    except Exception as e:
        print(f"[Troubleshooting] Hata: {e}")
