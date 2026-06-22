# -*- coding: utf-8 -*-
"""ReYMeN_cli/clipboard.py — Pano CLI.

Copy, paste, list, clear, history islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _pano_dosyasi() -> Path:
    """Pano verilerinin saklandigi dosya."""
    return PROJE_KOK / ".ReYMeN" / "clipboard" / "pano.json"


def _pano_oku() -> dict:
    """Pano icerigini oku."""
    dosya = _pano_dosyasi()
    if not dosya.exists():
        return {"aktif": "", "gecmis": []}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"aktif": "", "gecmis": []}
    except (json.JSONDecodeError, Exception):
        return {"aktif": "", "gecmis": []}


def _pano_yaz(veri: dict):
    """Pano icerigini yaz."""
    dosya = _pano_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Clipboard CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: copy, paste, list, clear, history
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["copy", "paste", "list", "clear", "history"],
                            help="Yapilacak islem (copy|paste|list|clear|history)")
    alt_parser.add_argument("--text", type=str, default=None,
                            help="Kopyalanacak metin (copy icin)")
    alt_parser.add_argument("--index", type=int, default=None,
                            help="Gecmis indeksi (paste icin)")


def calistir(args):
    """Clipboard komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "copy":
            text = args.text
            if not text:
                print("[Clipboard] Lutfen --text parametresini belirtin.")
                return
            pano = _pano_oku()
            if pano["aktif"]:
                pano["gecmis"].append(pano["aktif"])
            pano["aktif"] = text
            if len(pano["gecmis"]) > 50:
                pano["gecmis"] = pano["gecmis"][-50:]
            _pano_yaz(pano)
            print(f"[Clipboard] Kopyalandi ({len(text)} karakter)")

        elif islem == "paste":
            pano = _pano_oku()
            idx = args.index
            if idx is not None:
                if 0 <= idx < len(pano["gecmis"]):
                    icerik = pano["gecmis"][idx]
                    print(f"[Clipboard] Gecmis #{idx}:")
                    print(icerik)
                else:
                    print(f"[Clipboard] Gecersiz indeks: {idx}")
            else:
                if pano["aktif"]:
                    print(f"[Clipboard] Aktif pano icerigi:")
                    print(pano["aktif"])
                else:
                    print("[Clipboard] Pano bos.")

        elif islem == "list":
            pano = _pano_oku()
            print(f"[Clipboard] Pano durumu:")
            aktif_var = bool(pano["aktif"])
            print(f"  + Aktif: {'Var' if aktif_var else 'Bos'}")
            print(f"  + Gecmis: {len(pano['gecmis'])} kayit")
            if aktif_var:
                print(f"  + Boyut: {len(pano['aktif'])} karakter")

        elif islem == "clear":
            pano = _pano_oku()
            pano["aktif"] = ""
            pano["gecmis"] = []
            _pano_yaz(pano)
            print("[Clipboard] Pano temizlendi.")

        elif islem == "history":
            pano = _pano_oku()
            if not pano["gecmis"]:
                print("[Clipboard] Gecmis bos.")
            else:
                print(f"[Clipboard] Pano gecmisi ({len(pano['gecmis'])} kayit):")
                for i, kayit in enumerate(pano["gecmis"][-20:]):
                    ozet = kayit[:80] + "..." if len(kayit) > 80 else kayit
                    print(f"  #{i}: {ozet}")

    except Exception as e:
        print(f"[Clipboard] Beklenmeyen hata: {e}")
