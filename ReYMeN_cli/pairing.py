# -*- coding: utf-8 -*-
"""ReYMeN_cli/pairing.py — Eslestirme CLI.

List, pair, unpair, code, status islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _pairing_dosyasi() -> Path:
    """Eslestirme bilgi dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "pairing" / "devices.json"


def _pairing_oku() -> dict:
    """Kayitli cihazlari oku."""
    dosya = _pairing_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _pairing_yaz(veri: dict):
    """Cihaz bilgilerini yaz."""
    dosya = _pairing_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Pairing CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, pair, unpair, code, status
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "pair", "unpair", "code", "status"],
                            help="Yapilacak islem (list|pair|unpair|code|status)")
    alt_parser.add_argument("--device", type=str, default=None,
                            help="Cihaz adi/ID")
    alt_parser.add_argument("--host", type=str, default=None,
                            help="Cihaz host (pair icin)")
    alt_parser.add_argument("--port", type=int, default=None,
                            help="Cihaz port (pair icin)")


def calistir(args):
    """Pairing komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "list":
            cihazlar = _pairing_oku()
            if not cihazlar:
                print("[Pairing] Eslesmis cihaz yok.")
            else:
                print(f"[Pairing] Eslesmis cihazlar ({len(cihazlar)} adet):")
                for ad, bilgi in sorted(cihazlar.items()):
                    host = bilgi.get("host", "?")
                    port = bilgi.get("port", "?")
                    durum = bilgi.get("durum", "bagli")
                    print(f"  + {ad} ({host}:{port}) [{durum}]")

        elif islem == "pair":
            device = args.device
            host = args.host
            port = args.port
            if not device or not host:
                print("[Pairing] Lutfen --device ve --host parametrelerini belirtin.")
                return
            cihazlar = _pairing_oku()
            cihazlar[device] = {
                "host": host,
                "port": port or 9090,
                "durum": "bagli",
                "zaman": datetime.now().isoformat(),
            }
            _pairing_yaz(cihazlar)
            print(f"[Pairing] '{device}' eslestirildi ({host}:{port or 9090})")

        elif islem == "unpair":
            device = args.device
            if not device:
                print("[Pairing] Lutfen --device parametresini belirtin.")
                return
            cihazlar = _pairing_oku()
            if device not in cihazlar:
                print(f"[Pairing] Cihaz bulunamadi: {device}")
                return
            del cihazlar[device]
            _pairing_yaz(cihazlar)
            print(f"[Pairing] '{device}' eslestirmesi kaldirildi.")

        elif islem == "code":
            import random
            kod = str(random.randint(100000, 999999))
            print(f"[Pairing] Eslesme kodu: {kod}")
            kod_yolu = PROJE_KOK / ".ReYMeN" / "pairing" / "code.txt"
            kod_yolu.parent.mkdir(parents=True, exist_ok=True)
            with open(str(kod_yolu), "w", encoding="utf-8") as f:
                f.write(kod)

        elif islem == "status":
            cihazlar = _pairing_oku()
            print("[Pairing] Eslesme durumu:")
            print(f"  + Eslesmis cihaz: {len(cihazlar)}")
            for ad, bilgi in cihazlar.items():
                durum = bilgi.get("durum", "bilinmiyor")
                print(f"  + {ad}: {durum}")

    except Exception as e:
        print(f"[Pairing] Beklenmeyen hata: {e}")
