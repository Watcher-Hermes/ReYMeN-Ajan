# -*- coding: utf-8 -*-
"""ReYMeN_cli/dump.py — Dokum CLI.

Memory, config, state, tools, full islemleri.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

PROJE_KOK = Path(__file__).parent.parent


def _sistem_bilgisi() -> dict:
    """Temel sistem bilgilerini topla."""
    return {
        "zaman": datetime.now().isoformat(),
        "python": sys.version,
        "platform": sys.platform,
        "proje": str(PROJE_KOK),
    }


def kaydet(alt_parser):
    """Dump CLI alt komutlarini argparse alt ayristiricisina kaydet.

    Alt komutlar: memory, config, state, tools, full
    """
    alt_parser.add_argument("islem", type=str, nargs="?",
                            choices=["memory", "config", "state", "tools", "full"],
                            help="Yapilacak islem (memory|config|state|tools|full)")
    alt_parser.add_argument("--output", type=str, default=None,
                            help="Cikti dosyasi")


def calistir(args):
    """Dump komutunu calistir."""
    try:
        islem = args.islem or "full"
        output = args.output
        veri = _sistem_bilgisi()

        if islem in ("memory", "full"):
            print("[Dump] Hafiza bilgisi:")
            mem_bilgi = {
                "modul_sayisi": len(sys.modules),
                "moduller": sorted(sys.modules.keys())[:30],
            }
            veri["memory"] = mem_bilgi
            print(f"  + Modul sayisi: {mem_bilgi['modul_sayisi']}")

        if islem in ("config", "full"):
            print("[Dump] Config bilgisi:")
            config_dosyasi = PROJE_KOK / ".ReYMeN" / "config.json"
            config_veri = {}
            if config_dosyasi.exists():
                try:
                    with open(str(config_dosyasi), "r", encoding="utf-8") as f:
                        config_veri = json.loads(f.read())
                except Exception:
                    config_veri = {"hata": "Okunamadi"}
            veri["config"] = config_veri
            print(f"  + Config: {len(config_veri)} alan")

        if islem in ("state", "full"):
            print("[Dump] Durum bilgisi:")
            durum_bilgi = {
                "cwd": os.getcwd(),
                "kullanici": os.environ.get("USER", os.environ.get("USERNAME", "?")),
            }
            veri["state"] = durum_bilgi
            print(f"  + CWD: {durum_bilgi['cwd']}")

        if islem in ("tools", "full"):
            print("[Dump] Arac bilgisi:")
            arac_bilgi = {
                "mevcut_araclar": ["terminal", "read_file", "write_file", "search_files", "patch", "process"],
            }
            veri["tools"] = arac_bilgi
            print(f"  + Mevcut araclar: {len(arac_bilgi['mevcut_araclar'])}")

        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(veri, f, indent=2, ensure_ascii=False)
            print(f"[Dump] Kaydedildi: {output}")
        else:
            print(f"\n[Dump] Ozet:")
            for k in veri:
                if k != "zaman":
                    print(f"  + {k}: {'var' if veri.get(k) else 'yok'}")

    except Exception as e:
        print(f"[Dump] Beklenmeyen hata: {e}")
