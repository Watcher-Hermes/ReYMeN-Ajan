# -*- coding: utf-8 -*-
"""ReYMeN_cli/demo.py — Tanitim/Demo CLI.

Sistem ozelliklerini gosteren interaktif demo modu.
"""

import time
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _adim_yaz(baslik, icerik, bekle=0.5):
    """Adim adim demo gosterimi."""
    print(f"\n=== {baslik} ===")
    time.sleep(bekle)
    print(f"  {icerik}")
    time.sleep(bekle)


def kaydet(alt_parser):
    """demo CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["start", "quick", "features", "tour", "exit"],
                            help="Yapilacak islem (start|quick|features|tour|exit)")
    alt_parameter = alt_parser.add_argument("--speed", type=str, default="normal",
                                            choices=["slow", "normal", "fast"], help="Demo hizi")


def calistir(args):
    """demo komutunu calistir."""
    try:
        islem = args.islem or "quick"
        bekle = {"slow": 1.0, "normal": 0.5, "fast": 0.1}.get(args.speed, 0.5)

        print(f"[Demo] ReYMeN Sistemi Tanitimi")
        print(f"[Demo] Hiz: {args.speed}")

        if islem == "start":
            _adim_yaz("Hos Geldiniz", "ReYMeN projesine hos geldiniz!", bekle)
            _adim_yaz("Gateway", "26 dosya ile guclu mesaj gecidi", bekle)
            _adim_yaz("CLI", "85+ modul ile kapsamli yonetim", bekle)

        elif islem == "quick":
            print("\n[Demo] Hizli ozet:")
            print("  + Gateway: 26 dosya, 10+ platform")
            print("  + CLI: 85+ modul, genisletilebilir")
            print("  + ReYMeN: 175 modul ile uyumlu")
            print("  + ReYMeN: Ozgun Turkce kimlik")

        elif islem == "features":
            features = [
                ("Coklu Platform", "Telegram, WeCom, DingTalk, SMS..."),
                ("Akilli CLI", "85+ modul, otomatik tamamlama"),
                ("Guvenlik", "Sifreleme, yetkilendirme, KVKK uyum"),
                ("Performans", "Onbellek, izleme, metrik"),
                ("Yedekleme", "Otomatik yedek ve geri yukleme"),
            ]
            for baslik, aciklama in features:
                _adim_yaz(baslik, aciklama, bekle)

        elif islem == "tour":
            print("\n[Demo] Rehberli tur basliyor...")
            for i in range(5):
                print(f"  Adim {i+1}/5 - Sistem kesfi...")
                time.sleep(bekle)
            print("[Demo] Tur tamamlandi")

    except Exception as e:
        print(f"[Demo] Hata: {e}")
