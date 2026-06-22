# -*- coding: utf-8 -*-
"""ReYMeN_cli/mcp_security.py — MCP guvenlik CLI.

Scan, allow, deny, list, report islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _guvenlik_dosyasi() -> Path:
    """Guvenlik politika dosyasi."""
    return PROJE_KOK / ".ReYMeN" / "mcp" / "security.json"


def _guvenlik_oku() -> dict:
    """Guvenlik ayarlarini oku."""
    dosya = _guvenlik_dosyasi()
    if not dosya.exists():
        return {"izinli": [], "engellenen": [], "rapor": []}
    try:
        with open(str(dosya), "r", encoding="utf-8") as f:
            icerik = f.read().strip()
            return json.loads(icerik) if icerik else {"izinli": [], "engellenen": [], "rapor": []}
    except (json.JSONDecodeError, Exception):
        return {"izinli": [], "engellenen": [], "rapor": []}


def _guvenlik_yaz(veri: dict):
    """Guvenlik ayarlarini yaz."""
    dosya = _guvenlik_dosyasi()
    dosya.parent.mkdir(parents=True, exist_ok=True)
    with open(str(dosya), "w", encoding="utf-8") as f:
        json.dump(veri, f, indent=2, ensure_ascii=False)


def kaydet(alt_parser):
    """MCP Security CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: scan, allow, deny, list, report
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["scan", "allow", "deny", "list", "report"],
                            help="Yapilacak islem (scan|allow|deny|list|report)")
    alt_parser.add_argument("--name", type=str, default=None,
                            help="MCP/Arac adi")
    alt_parser.add_argument("--reason", type=str, default=None,
                            help="Gerekce")


def calistir(args):
    """MCP Security komutunu calistir."""
    try:
        islem = args.islem or "list"

        if islem == "scan":
            print("[MCP Security] MCP bilesenleri taranıyor...")
            guvenlik = _guvenlik_oku()
            mcpler = ["filesystem", "github", "obsidian", "terminal"]
            for mcp in mcpler:
                durum = "Izinli" if mcp in guvenlik.get("izinli", []) else "Bilinmeyen"
                if mcp in guvenlik.get("engellenen", []):
                    durum = "Engelli"
                print(f"  + {mcp}: {durum}")
            print("[MCP Security] Tarama tamam.")

        elif islem == "allow":
            name = args.name
            if not name:
                print("[MCP Security] Lutfen --name parametresini belirtin.")
                return
            guvenlik = _guvenlik_oku()
            if "izinli" not in guvenlik:
                guvenlik["izinli"] = []
            if name not in guvenlik["izinli"]:
                guvenlik["izinli"].append(name)
            if name in guvenlik.get("engellenen", []):
                guvenlik["engellenen"].remove(name)
            _guvenlik_yaz(guvenlik)
            print(f"[MCP Security] '{name}' izin verildi.")

        elif islem == "deny":
            name = args.name
            if not name:
                print("[MCP Security] Lutfen --name parametresini belirtin.")
                return
            guvenlik = _guvenlik_oku()
            if "engellenen" not in guvenlik:
                guvenlik["engellenen"] = []
            if name not in guvenlik["engellenen"]:
                guvenlik["engellenen"].append(name)
            if name in guvenlik.get("izinli", []):
                guvenlik["izinli"].remove(name)
            _guvenlik_yaz(guvenlik)
            print(f"[MCP Security] '{name}' engellendi.")

        elif islem == "list":
            guvenlik = _guvenlik_oku()
            print("[MCP Security] Guvenlik politikasi:")
            print(f"  + Izinli ({len(guvenlik.get('izinli', []))}):")
            for a in guvenlik.get("izinli", []):
                print(f"    - {a}")
            print(f"  + Engellenen ({len(guvenlik.get('engellenen', []))}):")
            for a in guvenlik.get("engellenen", []):
                print(f"    - {a}")

        elif islem == "report":
            guvenlik = _guvenlik_oku()
            print("[MCP Security] Guvenlik raporu:")
            print(f"  + Olusturma: {datetime.now().isoformat()}")
            print(f"  + Izinli arac: {len(guvenlik.get('izinli', []))}")
            print(f"  + Engellenen arac: {len(guvenlik.get('engellenen', []))}")
            print(f"  + Rapor kaydi: {len(guvenlik.get('rapor', []))}")

    except Exception as e:
        print(f"[MCP Security] Beklenmeyen hata: {e}")
