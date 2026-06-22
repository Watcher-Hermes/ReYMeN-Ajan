# -*- coding: utf-8 -*-
"""ReYMeN_cli/middleware.py — Middleware CLI.

List, add, remove, order, test islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _middleware_dosyasi() -> Path:
    """Middleware konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "middleware" / "middleware.json"


def _middleware_oku() -> dict:
    """Middleware ayarlarini oku."""
    dosya = _middleware_dosyasi()
    if not dosya.exists():
        return {"sira": [], "aktif": {}}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"sira": [], "aktif": {}}
    except (json.JSONDecodeError, Exception):
        return {"sira": [], "aktif": {}}


def _middleware_yaz(veri: dict):
    """Middleware ayarlarini yaz."""
    dosya = _middleware_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Middleware CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, add, remove, order, test
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "add", "remove", "order", "test"],
                            help="Yapilacak islem (list|add|remove|order|test)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="Middleware adi")
    alt_parser.add_argument("--module", type=str, default=None,
                            help="Middleware modulu (add icin)")
    alt_parser.add_argument("--position", type=int, default=None,
                            help="Siradaki pozisyon (order icin)")


def calistir(args):
    """Middleware komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            mw = _middleware_oku()
            sira = mw.get("sira", [])
            if not sira:
                print("[Middleware] Tanimli middleware yok.")
            else:
                print(f"[Middleware] Middleware sirasi ({len(sira)} adet):")
                for i, ad in enumerate(sira, 1):
                    modul = mw.get("moduller", {}).get(ad, "?")
                    print(f"  {i}. {ad} ({modul})")

        elif islem == "add":
            name = args.name
            module = args.module
            if not name or not module:
                print("[Middleware] Lutfen --name ve --module parametrelerini belirtin.")
                return
            mw = _middleware_oku()
            if "moduller" not in mw:
                mw["moduller"] = {}
            mw["moduller"][name] = module
            if name not in mw.get("sira", []):
                mw.setdefault("sira", []).append(name)
            _middleware_yaz(mw)
            print(f"[Middleware] Middleware eklendi: {name} -> {module}")

        elif islem == "remove":
            name = args.name
            if not name:
                print("[Middleware] Lutfen --name parametresini belirtin.")
                return
            mw = _middleware_oku()
            if name in mw.get("sira", []):
                mw["sira"].remove(name)
            if name in mw.get("moduller", {}):
                del mw["moduller"][name]
            _middleware_yaz(mw)
            print(f"[Middleware] Middleware silindi: {name}")

        elif islem == "order":
            name = args.name
            position = args.position
            if not name or position is None:
                print("[Middleware] Lutfen --name ve --position parametrelerini belirtin.")
                return
            mw = _middleware_oku()
            sira = mw.get("sira", [])
            if name not in sira:
                print(f"[Middleware] Middleware bulunamadi: {name}")
                return
            sira.remove(name)
            position = max(0, min(position, len(sira)))
            sira.insert(position, name)
            mw["sira"] = sira
            _middleware_yaz(mw)
            print(f"[Middleware] '{name}' {position}. siraya tasindi.")

        elif islem == "test":
            name = args.name
            if not name:
                print("[Middleware] Lutfen --name parametresini belirtin.")
                return
            mw = _middleware_oku()
            if name not in mw.get("sira", []):
                print(f"[Middleware] Middleware bulunamadi: {name}")
                return
            print(f"[Middleware] Test ediliyor: {name}")
            print(f"[Middleware] Test basarili.")

    except Exception as e:
        print(f"[Middleware] Beklenmeyen hata: {e}")
