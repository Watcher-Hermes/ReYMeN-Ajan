# -*- coding: utf-8 -*-
"""ReYMeN_cli/tips.py — Ipuclari CLI.

Show, random, search, add, daily islemleri.
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _tips_dosyasi() -> Path:
    """Ipucu veritabani dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "tips" / "tips.json"


def _tips_oku() -> dict:
    """Ipuclarini oku."""
    dosya = _tips_dosyasi()
    if not dosya.exists():
        return {"ipuclari": [], "gunluk": ""}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"ipuclari": [], "gunluk": ""}
    except (json.JSONDecodeError, Exception):
        return {"ipuclari": [], "gunluk": ""}


def _tips_yaz(veri: dict):
    """Ipuclarini yaz."""
    dosya = _tips_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Tips CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: show, random, search, add, daily
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["show", "random", "search", "add", "daily"],
                            help="Yapilacak islem (show|random|search|add|daily)")
    alt_parser.add_argument("--text", type=str, default=None,
                            help="Ipucu metni (add icin)")
    alt_parser.add_argument("--query", type=str, default=None,
                            help="Arama metni (search icin)")
    alt_parser.add_argument("--index", type=int, default=None,
                            help="Ipucu indeksi (show icin)")


def calistir(args):
    """Tips komutunu calistir."""
    try:
        islem = args.islem or "random"

        if islem == "show":
            tips = _tips_oku()
            ipuclari = tips.get("ipuclari", [])
            idx = args.index
            if idx is not None and 0 <= idx < len(ipuclari):
                print(f"[Tips] #{idx}: {ipuclari[idx]}")
            elif ipuclari:
                print(f"[Tips] Tum ipuclari ({len(ipuclari)} adet):")
                for i, tip in enumerate(ipuclari):
                    print(f"  #{i}: {tip}")
            else:
                print("[Tips] Henuz ipucu yok.")

        elif islem == "random":
            tips = _tips_oku()
            ipuclari = tips.get("ipuclari", [])
            if ipuclari:
                secilen = random.choice(ipuclari)
                print(f"[Tips] Rastgele ipucu: {secilen}")
            else:
                print("[Tips] Henuz ipucu yok. 'add' ile ekleyebilirsiniz.")

        elif islem == "search":
            query = args.query
            if not query:
                print("[Tips] Lutfen --query parametresini belirtin.")
                return
            tips = _tips_oku()
            ipuclari = tips.get("ipuclari", [])
            eslesenler = [t for t in ipuclari if query.lower() in t.lower()]
            if eslesenler:
                print(f"[Tips] '{query}' icin {len(eslesenler)} eslesme:")
                for tip in eslesenler:
                    print(f"  + {tip}")
            else:
                print(f"[Tips] '{query}' icin eslesme bulunamadi.")

        elif islem == "add":
            text = args.text
            if not text:
                print("[Tips] Lutfen --text parametresini belirtin.")
                return
            tips = _tips_oku()
            if "ipuclari" not in tips:
                tips["ipuclari"] = []
            tips["ipuclari"].append(text)
            _tips_yaz(tips)
            print(f"[Tips] Ipucu eklendi (sira: {len(tips['ipuclari'])}): {text}")

        elif islem == "daily":
            tips = _tips_oku()
            gunluk = tips.get("gunluk", "")
            if not gunluk:
                ipuclari = tips.get("ipuclari", [])
                if ipuclari:
                    gunluk = random.choice(ipuclari)
                    tips["gunluk"] = gunluk
                    tips["gunluk_tarih"] = datetime.now().strftime("%Y-%m-%d")
                    _tips_yaz(tips)
            if gunluk:
                print(f"[Tips] Gunun ipucu ({datetime.now().strftime('%d.%m.%Y')}):")
                print(f"  {gunluk}")
            else:
                print("[Tips] Gunluk ipucu ayarlanmadi. Once ipucu ekleyin.")

    except Exception as e:
        print(f"[Tips] Beklenmeyen hata: {e}")
