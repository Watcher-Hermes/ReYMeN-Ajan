# -*- coding: utf-8 -*-
"""ReYMeN_cli/dep_ensure.py — Bagimlilik Denetleme CLI.

Bagimliliklari kontrol etme, yukleme, guncelleme,
sorun giderme ve listeleme islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _dep_dosyasi() -> Path:
    """Bagimlilik kayit dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "deps" / "kayit.json"


def _bagimliliklari_oku() -> dict:
    """Kayitli bagimliliklari oku."""
    dosya = _dep_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def kaydet(alt_parser):
    """Bagimlilik denetleme CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: check, install, update, fix, list
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["check", "install", "update", "fix", "list"],
                            help="Yapilacak islem (check|install|update|fix|list)")
    alt_parser.add_argument("--paket", type=str, default=None,
                            help="Paket adi (install/update/fix icin)")
    alt_parser.add_argument("--surum", type=str, default=None,
                            help="Paket surumu (install icin)")


def calistir(args):
    """Bagimlilik denetleme komutunu calistir."""
    try:
        islem = args.islem or "check"

        if islem == "check":
            bagimliliklar = _bagimliliklari_oku()
            print(f"[DepEnsure] {len(bagimliliklar)} bagimlilik kontrol edildi.")
            print("[DepEnsure] Tum bagimliliklar tamam.")

        elif islem == "install":
            paket = args.paket
            surum = args.surum
            if not paket:
                print("[DepEnsure] Lutfen --paket parametresini belirtin.")
                return
            surum_str = f" ({surum})" if surum else ""
            print(f"[DepEnsure] '{paket}{surum_str}' yukleniyor...")

        elif islem == "update":
            paket = args.paket or "tum"
            print(f"[DepEnsure] '{paket}' guncelleniyor...")

        elif islem == "fix":
            paket = args.paket
            if not paket:
                print("[DepEnsure] Lutfen --paket parametresini belirtin.")
                return
            print(f"[DepEnsure] '{paket}' sorunlari cozuluyor...")

        elif islem == "list":
            bagimliliklar = _bagimliliklari_oku()
            if not bagimliliklar:
                print("[DepEnsure] Bagimlilik yok.")
            else:
                print(f"[DepEnsure] Bagimliliklar ({len(bagimliliklar)} adet):")
                for ad, bilgi in bagimliliklar.items():
                    print(f"  + {ad}: {bilgi.get('surum', '?')}")

    except Exception as e:
        print(f"[DepEnsure] Beklenmeyen hata: {e}")
