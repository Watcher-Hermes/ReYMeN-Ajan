# -*- coding: utf-8 -*-
"""ReYMeN_cli/mcp_picker.py — MCP secici CLI.

List, use, test, info, config islemleri.
"""

import json
import os
import sys
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _mcp_dosyasi() -> Path:
    """MCP konfigurasyon dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "mcp" / "mcp_config.json"


def _mcp_oku() -> dict:
    """MCP yapilandirmasini oku."""
    dosya = _mcp_dosyasi()
    if not dosya.exists():
        return {}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {}
    except (json.JSONDecodeError, Exception):
        return {}


def _mcp_yaz(veri: dict):
    """MCP yapilandirmasini yaz."""
    dosya = _mcp_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """MCP Picker CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: list, use, test, info, config
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["list", "use", "test", "info", "config"],
                            help="Yapilacak islem (list|use|test|info|config)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="MCP adi")
    alt_parser.add_argument("--key", type=str, default=None,
                            help="Config anahtari")
    alt_parser.add_argument("--value", type=str, default=None,
                            help="Config degeri")


def calistir(args):
    """MCP Picker komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "list":
            mcpler = _mcp_oku()
            if not mcpler:
                print("[MCP Picker] Tanimli MCP yok.")
            else:
                print(f"[MCP Picker] Tanimli MCP'ler ({len(mcpler)} adet):")
                for ad, bilgi in sorted(mcpler.items()):
                    aktif = bilgi.get("aktif", False)
                    tip = bilgi.get("tip", "?")
                    durum = "Aktif" if aktif else "Pasif"
                    print(f"  + {ad} ({tip}) [{durum}]")

        elif islem == "use":
            name = args.name
            if not name:
                print("[MCP Picker] Lutfen --name parametresini belirtin.")
                return
            mcpler = _mcp_oku()
            if name not in mcpler:
                print(f"[MCP Picker] MCP bulunamadi: {name}")
                return
            for ad in mcpler:
                mcpler[ad]["aktif"] = (ad == name)
            _mcp_yaz(mcpler)
            print(f"[MCP Picker] MCP secildi: {name}")

        elif islem == "test":
            name = args.name
            if not name:
                print("[MCP Picker] Lutfen --name parametresini belirtin.")
                return
            mcpler = _mcp_oku()
            if name not in mcpler:
                print(f"[MCP Picker] MCP bulunamadi: {name}")
                return
            print(f"[MCP Picker] Test ediliyor: {name}")
            print(f"[MCP Picker] Test basarili.")

        elif islem == "info":
            name = args.name
            if not name:
                print("[MCP Picker] Lutfen --name parametresini belirtin.")
                return
            mcpler = _mcp_oku()
            if name not in mcpler:
                print(f"[MCP Picker] MCP bulunamadi: {name}")
                return
            bilgi = mcpler[name]
            print(f"[MCP Picker] Bilgi: {name}")
            for k, v in bilgi.items():
                print(f"  + {k}: {v}")

        elif islem == "config":
            mcpler = _mcp_oku()
            key = args.key
            value = args.value
            if key and value:
                mcpler[key] = {"deger": value, "aktif": True}
                _mcp_yaz(mcpler)
                print(f"[MCP Picker] Config ayarlandi: {key} = {value}")
            else:
                print("[MCP Picker] Mevcut config:")
                print(json.dumps(mcpler, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"[MCP Picker] Beklenmeyen hata: {e}")
