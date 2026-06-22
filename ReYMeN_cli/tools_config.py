# -*- coding: utf-8 -*-
"""ReYMeN_cli/tools_config.py — Tool yapilandirma CLI.

List, get, set, reset, export islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _tools_dosyasi() -> Path:
    """Tool konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "tools" / "tools_config.json"


def _tools_oku() -> dict:
    """Tool ayarlarini oku."""
    dosya = _tools_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _tools_yaz(veri: dict):
    """Tool ayarlarini yaz."""
    dosya = _tools_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """Tools Config CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, get, set, reset, export
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "get", "set", "reset", "export"],
                            help="Yapilacak islem (list|get|set|reset|export)")
    alt_parser.add_argument("--tool", type=str, default=None,
                            help="Arac adi")
    alt_parser.add_argument("--key", type=str, default=None,
                            help="Yapilandirma anahtari")
    alt_parser.add_argument("--value", type=str, default=None,
                            help="Yapilandirma degeri")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi (export icin)")


def calistir(args):
    """Tools Config komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            tools = _tools_oku()
            if not tools:
                print("[Tools Config] Yapilandirilmis arac yok.")
            else:
                print(f"[Tools Config] Yapilandirilmis araclar ({len(tools)} adet):")
                for ad, ayarlar in sorted(tools.items()):
                    print(f"  + {ad}: {len(ayarlar)} ayar")

        elif islem == "get":
            tool = args.tool
            key = args.key
            if not tool:
                print("[Tools Config] Lutfen --tool parametresini belirtin.")
                return
            tools = _tools_oku()
            if tool not in tools:
                print(f"[Tools Config] Arac bulunamadi: {tool}")
                return
            if key:
                deger = tools[tool].get(key, "Bulunamadi")
                print(f"[Tools Config] {tool}.{key} = {deger}")
            else:
                print(f"[Tools Config] '{tool}' ayarlari:")
                for k, v in tools[tool].items():
                    print(f"  + {k}: {v}")

        elif islem == "set":
            tool = args.tool
            key = args.key
            value = args.value
            if not tool or not key or value is None:
                print("[Tools Config] Lutfen --tool, --key ve --value parametrelerini belirtin.")
                return
            tools = _tools_oku()
            if tool not in tools:
                tools[tool] = {}
            tools[tool][key] = value
            _tools_yaz(tools)
            print(f"[Tools Config] '{tool}.{key}' ayarlandi: {value}")

        elif islem == "reset":
            tool = args.tool
            if not tool:
                print("[Tools Config] Lutfen --tool parametresini belirtin.")
                return
            tools = _tools_oku()
            if tool in tools:
                del tools[tool]
                _tools_yaz(tools)
                print(f"[Tools Config] '{tool}' sifirlandi.")
            else:
                print(f"[Tools Config] Arac bulunamadi: {tool}")

        elif islem == "export":
            tools = _tools_oku()
            output = args.output or str(PROJE_KOK / ".ReYMeN" / "tools" / f"tools_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(output, "w", encoding="utf-8") as f:
                json.dump(tools, f, indent=2, ensure_ascii=False)
            print(f"[Tools Config] Export edildi: {output}")

    except Exception as e:
        print(f"[Tools Config] Beklenmeyen hata: {e}")
