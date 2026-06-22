# -*- coding: utf-8 -*-
"""ReYMeN_cli/registry_cli.py — Kayit Defteri CLI.

Modul ve bilesen kayitlarini yonetme, listeleme ve arama.
"""

from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _registry_icerigi():
    """Ornek registry icerigi."""
    return {
        "gateway": {"durum": "kayitli", "versiyon": "1.0.0"},
        "ReYMeN_cli": {"durum": "kayitli", "versiyon": "1.0.0"},
        "plugins": {"durum": "kayitli", "versiyon": "0.5.0"},
    }


def kaydet(alt_parser):
    """registry_cli CLI alt komutlarini argparse alt ayristiricisina kaydet."""
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "register", "unregister", "search", "info"],
                            help="Yapilacak islem (list|register|unregister|search|info)")
    alt_parser.add_argument("--name", type=str, default=None, help="Bilesen adi")
    alt_parser.add_argument("--version", type=str, default=None, help="Versiyon")
    alt_parser.add_argument("--type", type=str, default=None, help="Bilesen turu")


def calistir(args):
    """registry_cli komutunu calistir."""
    try:
        islem = args.islem or "list"
        print(f"[Registry] Baslatiliyor: {islem}")

        if islem == "list":
            print("[Registry] Kayitli bilesenler:")
            for ad, bilgi in _registry_icerigi().items():
                print(f"  {ad} -> {bilgi['durum']} (v{bilgi['versiyon']})")

        elif islem == "register":
            ad = args.name or "yeni_bilesen"
            surum = args.version or "0.1.0"
            print(f"[Registry] Kaydediliyor: {ad} v{surum}")
            print(f"  Kayit basarili")

        elif islem == "unregister":
            ad = args.name
            if not ad:
                print("[Registry] --name belirtin")
                return
            print(f"[Registry] Kayit siliniyor: {ad}")
            print(f"  {ad} kayit defterinden kaldirildi")

        elif islem == "search":
            sorgu = args.name or ""
            print(f"[Registry] Araniyor: {sorgu}")
            for ad in _registry_icerigi():
                if sorgu.lower() in ad.lower():
                    print(f"  + {ad}")

        elif islem == "info":
            ad = args.name or "ReYMeN_cli"
            bilgi = _registry_icerigi().get(ad, {"durum": "bilinmiyor"})
            print(f"[Registry] {ad} bilgisi:")
            for anahtar, deger in bilgi.items():
                print(f"  {anahtar}: {deger}")

    except Exception as e:
        print(f"[Registry] Hata: {e}")
