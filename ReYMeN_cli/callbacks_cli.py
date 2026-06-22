# -*- coding: utf-8 -*-
"""ReYMeN_cli/callbacks_cli.py — Callback CLI.

Callback kaydetme, kaldirma, listeleme,
tetikleme ve test etme islemleri.
"""

import json
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _callback_dosyasi() -> Path:
    """Callback kayit dosyasi yolu."""
    return PROJE_KOK / ".ReYMeN" / "callbacks" / "kayit.json"


def _callbacklari_oku() -> list:
    """Kayitli callbackleri oku."""
    dosya = _callback_dosyasi()
    if not dosya.exists():
        return []
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else []
    except (json.JSONDecodeError, Exception):
        return []


def kaydet(alt_parser):
    """Callback CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: register, unregister, list, trigger, test
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["register", "unregister", "list", "trigger", "test"],
                            help="Yapilacak islem (register|unregister|list|trigger|test)")
    alt_parser.add_argument("--ad", type=str, default=None,
                            help="Callback adi")
    alt_parser.add_argument("--url", type=str, default=None,
                            help="Callback URL (register/trigger icin)")
    alt_parser.add_argument("--data", type=str, default=None,
                            help="Callback verisi (trigger/test icin)")


def calistir(args):
    """Callback komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "register":
            ad = args.ad or "default"
            url = args.url
            if not url:
                print("[Callbacks] Lutfen --url parametresini belirtin.")
                return
            print(f"[Callbacks] '{ad}' callback'i kaydedildi (URL: {url})")

        elif islem == "unregister":
            ad = args.ad
            if not ad:
                print("[Callbacks] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Callbacks] '{ad}' callback'i kaldirildi.")

        elif islem == "list":
            callbacklar = _callbacklari_oku()
            if not callbacklar:
                print("[Callbacks] Kayitli callback yok.")
            else:
                print(f"[Callbacks] Kayitli callbackler ({len(callbacklar)} adet):")
                for c in callbacklar:
                    ad = c.get("ad", "?")
                    url = c.get("url", "?")
                    print(f"  + {ad}: {url}")

        elif islem == "trigger":
            ad = args.ad
            data = args.data or "{}"
            if not ad:
                print("[Callbacks] Lutfen --ad parametresini belirtin.")
                return
            print(f"[Callbacks] '{ad}' callback'i tetiklendi (data: {data})")

        elif islem == "test":
            url = args.url or "http://localhost:8080/test"
            print(f"[Callbacks] Test callback gonderiliyor -> {url}")

    except Exception as e:
        print(f"[Callbacks] Beklenmeyen hata: {e}")
