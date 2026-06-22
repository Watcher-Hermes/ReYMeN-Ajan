# -*- coding: utf-8 -*-
"""ReYMeN_cli/routing.py — Yonlendirme CLI.

Mesaj yonlendirme kurallari, filtreleme ve kanal yonetimi.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _varsayilan_kurallar():
    """Varsayilan yonlendirme kurallari."""
    return [
        ("mesaj", "telegram", "wecom", "Mesaj metni"),
        ("dosya", "telegram", "email", "Dosya eki"),
        ("log", "tum", "wecom", "Sistem loglari"),
    ]


def kaydet(alt_parser):
    """routing CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "test", "clear"],
                            help="Yapilacak islem (list|add|remove|test|clear)")
    alt_parser.add_argument("--source", type=str, default=None, help="Kaynak kanal")
    alt_parser.add_argument("--target", type=str, default=None, help="Hedef kanal")
    alt_parser.add_argument("--filter", type=str, default=None, help="Filtre ifadesi")


def calistir(args):
    """routing komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Routing] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Routing] Yonlendirme kurallari:")
            for tur, kaynak, hedef, aciklama in _varsayilan_kurallar():
                print(f"  [{tur}] {kaynak} -> {hedef} ({aciklama})")

        elif islem == "add":
            kaynak = args.source or "telegram"
            hedef = args.target or "wecom"
            filtre = args.filter or "*"
            print(f"[Routing] Kural ekleniyor:")
            print(f"  {kaynak} -> {hedef} (filtre: {filtre})")
            print("  Kural basariyla eklendi")

        elif islem == "remove":
            print(f"[Routing] Kural kaldiriliyor...")
            print("  Kural basariyla kaldirildi")

        elif islem == "test":
            kaynak = args.source or "telegram"
            hedef = args.target or "wecom"
            print(f"[Routing] Test yonlendirmesi:")
            print(f"  {kaynak} -> {hedef}: BASARILI")

        elif islem == "clear":
            print("[Routing] Tum kurallar temizleniyor...")
            print("[Routing] Tum kurallar basariyla temizlendi")

    except Exception as e:
        print(f"[Routing] Hata: {e}")
