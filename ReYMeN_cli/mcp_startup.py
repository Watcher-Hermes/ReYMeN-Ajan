# -*- coding: utf-8 -*-
"""ReYMeN_cli/mcp_startup.py — MCP baslangic CLI.

List, enable, disable, order, status islemleri.
"""

import json
import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _startup_dosyasi() -> Path:
    """MCP baslangic konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "mcp" / "startup.json"


def _startup_oku() -> dict:
    """Baslangic ayarlarini oku."""
    dosya = _startup_dosyasi()
    if not dosya.exists():
        return {"sira": [], "aktif": {}}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"sira": [], "aktif": {}}
    except (json.JSONDecodeError, Exception):
        return {"sira": [], "aktif": {}}


def _startup_yaz(veri: dict):
    """Baslangic ayarlarini yaz."""
    dosya = _startup_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """MCP Startup CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, enable, disable, order, status
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "enable", "disable", "order", "status"],
                            help="Yapilacak islem (list|enable|disable|order|status)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="MCP adi")
    alt_parser.add_argument("--position", type=int, default=None,
                            help="Siradaki pozisyon (order icin)")


def calistir(args):
    """MCP Startup komutunu calistir."""
    try:
        islem = args.islem or "status"

        if islem == "list":
            startup = _startup_oku()
            sira = startup.get("sira", [])
            if not sira:
                print("[MCP Startup] Baslangic sirasi bos.")
            else:
                print(f"[MCP Startup] Baslangic sirasi ({len(sira)} adet):")
                for i, ad in enumerate(sira, 1):
                    aktif = startup.get("aktif", {}).get(ad, True)
                    durum = "Aktif" if aktif else "Pasif"
                    print(f"  {i}. {ad} [{durum}]")

        elif islem == "enable":
            name = args.name
            if not name:
                print("[MCP Startup] Lutfen --name parametresini belirtin.")
                return
            startup = _startup_oku()
            if "aktif" not in startup:
                startup["aktif"] = {}
            startup["aktif"][name] = True
            if name not in startup.get("sira", []):
                startup.setdefault("sira", []).append(name)
            _startup_yaz(startup)
            print(f"[MCP Startup] '{name}' baslangica eklendi/aktif edildi.")

        elif islem == "disable":
            name = args.name
            if not name:
                print("[MCP Startup] Lutfen --name parametresini belirtin.")
                return
            startup = _startup_oku()
            if "aktif" in startup:
                startup["aktif"][name] = False
            _startup_yaz(startup)
            print(f"[MCP Startup] '{name}' baslangictan kaldirildi.")

        elif islem == "order":
            name = args.name
            position = args.position
            if not name or position is None:
                print("[MCP Startup] Lutfen --name ve --position parametrelerini belirtin.")
                return
            startup = _startup_oku()
            sira = startup.get("sira", [])
            if name in sira:
                sira.remove(name)
            position = max(0, min(position, len(sira)))
            sira.insert(position, name)
            startup["sira"] = sira
            _startup_yaz(startup)
            print(f"[MCP Startup] '{name}' {position}. siraya tasindi.")

        elif islem == "status":
            startup = _startup_oku()
            sira = startup.get("sira", [])
            print("[MCP Startup] Baslangic durumu:")
            print(f"  + Kayitli bilesen: {len(sira)}")
            aktif_say = sum(1 for a in sira if startup.get("aktif", {}).get(a, True))
            print(f"  + Aktif: {aktif_say}")
            print(f"  + Pasif: {len(sira) - aktif_say}")

    except Exception as e:
        print(f"[MCP Startup] Beklenmeyen hata: {e}")
