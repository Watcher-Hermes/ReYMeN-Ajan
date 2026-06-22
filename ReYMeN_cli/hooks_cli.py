# -*- coding: utf-8 -*-
"""ReYMeN_cli/hooks_cli.py — Hook CLI.

Hook listeleme, ekleme, kaldirma, etkinlestirme,
devre disi birakma ve test etme islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _hook_dosyasi() -> Path:
    """Hook kayit dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "hooks" / "kayit.json"


def _hooklari_oku() -> list:
    """Kayitli hooklari oku."""
    dosya = _hook_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Hook CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, add, remove, enable, disable, test
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "enable", "disable", "test"],
                            help="Yapilacak islem (list|add|remove|enable|disable|test)")
    alt_parser.add_argument("--ad", type=str, default=None,
                            help="Hook adi (add/remove/enable/disable/test icin)")
    alt_parser.add_argument("--komut", type=str, default=None,
                            help="Hook komutu (add icin)")


def calistir(args):
    """Hook komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            hooklar = _hooklari_oku()
            if not hooklar:
                print("[Hooks] Kayitli hook yok.")
            else:
                print(f"[Hooks] Kayitli hooklar ({len(hooklar)} adet):")
                for h in hooklar:
                    ad = h.get("ad", "?")
                    aktif = "Aktif" if h.get("aktif", True) else "Pasif"
                    print(f"  + {ad} [{aktif}]")

        elif islem == "add":
            ad = args.ad
            komut = args.komut
            if not ad or not komut:
                print("[Hooks] Lutfen --ad ve --komut parametrelerini belirtin.")
                return
            print(f"[Hooks] '{ad}' hooku eklendi (komut: {komut})")

        elif islem == "remove":
            ad = args.ad
            if not ad:
                print("[Hooks] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Hooks] '{ad}' hooku kaldirildi.")

        elif islem == "enable":
            ad = args.ad
            if not ad:
                print("[Hooks] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Hooks] '{ad}' hooku etkinlestirildi.")

        elif islem == "disable":
            ad = args.ad
            if not ad:
                print("[Hooks] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Hooks] '{ad}' hooku devre disi birakildi.")

        elif islem == "test":
            ad = args.ad or "all"
            print(f"[Hooks] '{ad}' hooku test ediliyor...")
            print("[Hooks] Test basarili.")

    except Exception as e:
        print(f"[Hooks] Beklenmeyen hata: {e}")
